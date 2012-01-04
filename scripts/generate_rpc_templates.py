#!/usr/bin/env python
import sys

"""This script is used to generate the mailbox templates in
`rethinkdb/src/rpc/mailbox/typed.hpp`. It is meant to be run as follows
(assuming that the current directory is `rethinkdb/src/`):

$ ../scripts/generate_rpc_templates.py > rpc/mailbox/typed.hpp

"""

def generate_async_message_template(nargs):

    def csep(template):
        return ", ".join(template.replace("#", str(i)) for i in xrange(nargs))

    def cpre(template):
        return "".join(", " + template.replace("#", str(i)) for i in xrange(nargs))

    print "template<" + csep("class arg#_t") + ">" 
    print "class async_mailbox_t< void(" + csep("arg#_t") + ") > {"
    print
    print "public:"
    print "    async_mailbox_t(mailbox_cluster_t *cluster, const boost::function< void(" + csep("arg#_t") + ") > &fun) :"
    print "        callback(fun),"
    print "        mailbox(cluster, boost::bind(&async_mailbox_t::on_message, this, _1, _2))"
    print "        { }"
    print
    print "    class address_t {"
    print "    public:"
    print "        bool is_nil() { return addr.is_nil(); }"
    print "        peer_id_t get_peer() { return addr.get_peer(); }"
    print "        RDB_MAKE_ME_SERIALIZABLE_1(addr)"
    print "    private:"
    print "        friend class async_mailbox_t;"
    if nargs == 0:
        print "        friend void send(mailbox_cluster_t*, address_t);"
    else:
        print "        template<" + csep("class a#_t") + ">"
        print "        friend void send(mailbox_cluster_t*, typename async_mailbox_t< void(" + csep("a#_t") + ") >::address_t" + cpre("const a#_t&") + ");"
    print "        mailbox_t::address_t addr;"
    print "    };"
    print
    print "    address_t get_address() {"
    print "        address_t a;"
    print "        a.addr = mailbox.get_address();"
    print "        return a;"
    print "    }"
    print
    print "private:"
    if nargs == 0:
        print "    friend void send(mailbox_cluster_t*, address_t);"
    else:
        print "    template<" + csep("class a#_t") + ">"
        print "    friend void send(mailbox_cluster_t*, typename async_mailbox_t< void(" + csep("a#_t") + ") >::address_t" + cpre("const a#_t&") + ");"
    print "    static void write(std::ostream &stream" + cpre("const arg#_t &arg#") + ") {"
    print "        boost::archive::binary_oarchive archive(stream);"
    for i in xrange(nargs):
        print "        archive << arg%d;" % i
    print "    }"
    print "    void on_message(std::istream &stream, const boost::function<void()> &done) {"
    for i in xrange(nargs):
        print "        arg%d_t arg%d;" % (i, i)
    print "        {"
    print "            boost::archive::binary_iarchive archive(stream);"
    for i in xrange(nargs):
        print "        archive >> arg%d;" % i
    print "        }"
    print "        done();"
    print "        callback(" + csep("arg#") + ");"
    print "    }"
    print
    print "    boost::function< void(" + csep("arg#_t") + ") > callback;"
    print "    mailbox_t mailbox;"
    print "};"
    print
    if nargs == 0:
        print "inline"
    else:
        print "template<" + csep("class arg#_t") + ">"
    print "void send(mailbox_cluster_t *src, " + ("typename " if nargs > 0 else "") + "async_mailbox_t< void(" + csep("arg#_t") + ") >::address_t dest" + cpre("const arg#_t &arg#") + ") {"
    print "    send(src, dest.addr,"
    print "        boost::bind(&async_mailbox_t< void(" + csep("arg#_t") + ") >::write, _1" + cpre("arg#") + "));"
    print "}"
    print

if __name__ == "__main__":

    print "#ifndef __RPC_MAILBOX_TYPED_HPP__"
    print "#define __RPC_MAILBOX_TYPED_HPP__"
    print

    print "/* This file is automatically generated by '%s'." % " ".join(sys.argv)
    print "Please modify '%s' instead of modifying this file.*/" % sys.argv[0]
    print

    print "#include \"errors.hpp\""
    print "#include <boost/archive/binary_iarchive.hpp>"
    print "#include <boost/archive/binary_oarchive.hpp>"
    print "#include \"rpc/serialize_macros.hpp\""
    print "#include \"rpc/mailbox/mailbox.hpp\""
    print

    print "template<class invalid_proto_t> class async_mailbox_t {"
    print "    /* If someone tries to instantiate `async_mailbox_t` "
    print "    incorrectly, this should cause an error. */"
    print "    typename invalid_proto_t::you_are_using_async_mailbox_t_incorrectly foo;"
    print "};"
    print

    for nargs in xrange(15):
        generate_async_message_template(nargs)

    print "#endif /* __RPC_MAILBOX_TYPED_HPP__ */"