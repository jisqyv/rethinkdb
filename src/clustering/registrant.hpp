#ifndef __CLUSTERING_REGISTRANT_HPP__
#define __CLUSTERING_REGISTRANT_HPP__

#include "clustering/registration_metadata.hpp"
#include "rpc/semilattice/metadata.hpp"
#include "rpc/mailbox/typed.hpp"

template<class data_t>
class registrant_t {

public:
    /* This constructor registers with the given registrant. If the registrant
    is already dead, it throws an exception. Otherwise, it returns immediately.
    */
    registrant_t(
            mailbox_manager_t *cl,
            boost::shared_ptr<semilattice_read_view_t<resource_metadata_t<registrar_metadata_t<data_t> > > > registrar_md,
            data_t initial_value)
            THROWS_ONLY(resource_lost_exc_t) :
        cluster(cl),
        registrar(cluster, registrar_md),
        registration_id(generate_uuid())
    {
        /* This will make it so that we get deregistered in our destructor. */
        deregisterer.fun = boost::bind(&registrant_t::send_deregister_message,
            cluster,
            registrar.access().delete_mailbox,
            registration_id);

        /* Send a message to register us */
        send(cluster, registrar.access().create_mailbox,
            registration_id,
            cluster->get_me(),
            initial_value);
    }

    /* The destructor deregisters us and returns immediately. It never throws
    any exceptions. */
    ~registrant_t() THROWS_NOTHING {

        /* Most of the work is done by the destructor for `deregisterer` */
    }

    signal_t *get_failed_signal() THROWS_NOTHING {
        return registrar.get_failed_signal();
    }

    std::string get_failed_reason() THROWS_NOTHING {
        rassert(get_failed_signal()->is_pulsed());
        return registrar.get_failed_reason();
    }

private:
    typedef typename registrar_metadata_t<data_t>::registration_id_t registration_id_t;

    /* We can't deregister in our destructor because then we wouldn't get
    deregistered if we died mid-constructor. Instead, the deregistration must be
    done by a separate subcomponent. `deregisterer` is that subcomponent. The
    constructor sets `deregisterer.fun` to a `boost::bind()` of
    `send_deregister_message()`, and that deregisters things as necessary. */
    static void send_deregister_message(
            mailbox_manager_t *cluster,
            typename registrar_metadata_t<data_t>::delete_mailbox_t::address_t addr,
            registration_id_t rid) THROWS_NOTHING {
        send(cluster, addr, rid);
    }
    death_runner_t deregisterer;

    mailbox_manager_t *cluster;
    resource_access_t<registrar_metadata_t<data_t> > registrar;
    registration_id_t registration_id;
};

#endif /* __CLUSTERING_REGISTRANT_HPP__ */