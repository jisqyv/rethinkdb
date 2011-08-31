#include "concurrency/cond_var.hpp"

#include "errors.hpp"
#include <boost/bind.hpp>

#include "arch/runtime/runtime.hpp"
#include "do_on_thread.hpp"

void cond_t::pulse() {
    do_on_thread(home_thread(), boost::bind(&cond_t::do_pulse, this));
}

void cond_t::do_pulse() {
    signal_t::pulse();
}

void one_waiter_cond_t::pulse() {
    rassert(!pulsed_);
    pulsed_ = true;
    if (waiter_) {
        coro_t *tmp = waiter_;
        waiter_ = NULL;
        tmp->notify_now();
        // we might be destroyed here
    }
}

void one_waiter_cond_t::wait_eagerly() {
    rassert(!waiter_);
    if (!pulsed_) {
        waiter_ = coro_t::self();
        coro_t::wait();
        rassert(pulsed_);
    }
}