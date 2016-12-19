'use strict';
var k = "function" == typeof Object.defineProperties ? Object.defineProperty : function(a, b, c) {
        if (c.get || c.set) throw new TypeError("ES3 does not support getters and setters.");
        a != Array.prototype && a != Object.prototype && (a[b] = c.value)
    },
    l = "undefined" != typeof window && window === this ? this : "undefined" != typeof global && null != global ? global : this;

function m() {
    m = function() {};
    l.d || (l.d = n)
}
var p = 0;

function n(a) {
    return "jscomp_symbol_" + (a || "") + p++
}

function q() {
    m();
    var a = l.d.iterator;
    a || (a = l.d.iterator = l.d("iterator"));
    "function" != typeof Array.prototype[a] && k(Array.prototype, a, {
        configurable: !0,
        writable: !0,
        value: function() {
            return r(this)
        }
    });
    q = function() {}
}

function r(a) {
    var b = 0;
    return t(function() {
        return b < a.length ? {
            done: !1,
            value: a[b++]
        } : {
            done: !0
        }
    })
}

function t(a) {
    q();
    a = {
        next: a
    };
    a[l.d.iterator] = function() {
        return this
    };
    return a
}

function u(a) {
    q();
    var b = a[Symbol.iterator];
    return b ? b.call(a) : r(a)
}
for (var v = l, w = ["Promise"], x = 0; x < w.length - 1; x++) {
    var y = w[x];
    y in v || (v[y] = {});
    v = v[y]
}
var z = w[w.length - 1],
    A = v[z],
    B = function() {
        function a(a) {
            this.b = 0;
            this.g = void 0;
            this.a = [];
            var d = this.e();
            try {
                a(d.resolve, d.reject)
            } catch (g) {
                d.reject(g)
            }
        }

        function b() {
            this.a = null
        }
        if (A) return A;
        b.prototype.b = function(a) {
            null == this.a && (this.a = [], this.e());
            this.a.push(a)
        };
        b.prototype.e = function() {
            var a = this;
            this.c(function() {
                a.g()
            })
        };
        var c = l.setTimeout;
        b.prototype.c = function(a) {
            c(a, 0)
        };
        b.prototype.g = function() {
            for (; this.a && this.a.length;) {
                var a = this.a;
                this.a = [];
                for (var b = 0; b < a.length; ++b) {
                    var c = a[b];
                    delete a[b];
                    try {
                        c()
                    } catch (h) {
                        this.f(h)
                    }
                }
            }
            this.a = null
        };
        b.prototype.f = function(a) {
            this.c(function() {
                throw a;
            })
        };
        a.prototype.e = function() {
            function a(a) {
                return function(d) {
                    c || (c = !0, a.call(b, d))
                }
            }
            var b = this,
                c = !1;
            return {
                resolve: a(this.l),
                reject: a(this.f)
            }
        };
        a.prototype.l = function(b) {
            if (b === this) this.f(new TypeError("A Promise cannot resolve to itself"));
            else if (b instanceof a) this.m(b);
            else {
                var d;
                a: switch (typeof b) {
                    case "object":
                        d = null != b;
                        break a;
                    case "function":
                        d = !0;
                        break a;
                    default:
                        d = !1
                }
                d ? this.k(b) : this.h(b)
            }
        };
        a.prototype.k = function(a) {
            var b = void 0;
            try {
                b = a.then
            } catch (g) {
                this.f(g);
                return
            }
            "function" == typeof b ? this.n(b, a) : this.h(a)
        };
        a.prototype.f = function(a) {
            this.i(2, a)
        };
        a.prototype.h = function(a) {
            this.i(1, a)
        };
        a.prototype.i = function(a, b) {
            if (0 != this.b) throw Error("Cannot settle(" + a + ", " + b | "): Promise already settled in state" + this.b);
            this.b = a;
            this.g = b;
            this.j()
        };
        a.prototype.j = function() {
            if (null != this.a) {
                for (var a = this.a, b = 0; b < a.length; ++b) a[b].call(), a[b] = null;
                this.a = null
            }
        };
        var f = new b;
        a.prototype.m = function(a) {
            var b = this.e();
            a.c(b.resolve, b.reject)
        };
        a.prototype.n = function(a, b) {
            var c = this.e();
            try {
                a.call(b, c.resolve, c.reject)
            } catch (h) {
                c.reject(h)
            }
        };
        a.prototype.then = function(b, c) {
            function d(a, b) {
                return "function" == typeof a ? function(b) {
                    try {
                        e(a(b))
                    } catch (L) {
                        f(L)
                    }
                } : b
            }
            var e, f, M = new a(function(a, b) {
                e = a;
                f = b
            });
            this.c(d(b, e), d(c, f));
            return M
        };
        a.prototype.catch = function(a) {
            return this.then(void 0, a)
        };
        a.prototype.c = function(a, b) {
            function c() {
                switch (d.b) {
                    case 1:
                        a(d.g);
                        break;
                    case 2:
                        b(d.g);
                        break;
                    default:
                        throw Error("Unexpected state: " + d.b);
                }
            }
            var d = this;
            null == this.a ? f.b(c) : this.a.push(function() {
                f.b(c)
            })
        };
        a.resolve = function(b) {
            return b instanceof a ? b : new a(function(a) {
                a(b)
            })
        };
        a.reject = function(b) {
            return new a(function(a, c) {
                c(b)
            })
        };
        a.b = function(b) {
            return new a(function(c, d) {
                for (var e = u(b), f = e.next(); !f.done; f = e.next()) a.resolve(f.value).c(c, d)
            })
        };
        a.a = function(b) {
            var c = u(b),
                d = c.next();
            return d.done ? a.resolve([]) : new a(function(b, e) {
                function f(a) {
                    return function(c) {
                        g[a] = c;
                        h--;
                        0 == h && b(g)
                    }
                }
                var g = [],
                    h = 0;
                do g.push(void 0), h++, a.resolve(d.value).c(f(g.length - 1), e), d = c.next(); while (!d.done)
            })
        };
        a.$jscomp$new$AsyncExecutor = function() {
            return new b
        };
        return a
    }();
B != A && null != B && k(v, z, {
    configurable: !0,
    writable: !0,
    value: B
});
var C = Date.now || function() {
    return +new Date
};
var D = null;

function E(a, b) {
    var c = {};
    c.key = a;
    c.value = b;
    F().then(function(a) {
        return new Promise(function(b, e) {
            var d = a.transaction("swpushnotificationsstore", "readwrite").objectStore("swpushnotificationsstore").put(c);
            d.onsuccess = b;
            d.onerror = e
        })
    })
}

function G(a) {
    return F().then(function(b) {
        return new Promise(function(c, f) {
            var d = b.transaction("swpushnotificationsstore").objectStore("swpushnotificationsstore").get(a);
            d.onsuccess = function() {
                var a = d.result;
                c(a ? a.value : null)
            };
            d.onerror = function() {
                f('Unable to get key "' + a + '" from object store.')
            }
        })
    }).catch(function() {
        return Promise.reject("Unable to open IndexedDB.")
    })
}

function F() {
    return D ? Promise.resolve(D) : new Promise(function(a, b) {
        var c = self.indexedDB.open("swpushnotificationsdb");
        c.onerror = b;
        c.onsuccess = function() {
            var b = c.result;
            if (b.objectStoreNames.contains("swpushnotificationsstore")) D = b, a(D);
            else return self.indexedDB.deleteDatabase("swpushnotificationsdb"), F()
        };
        c.onupgradeneeded = H
    })
}

function H(a) {
    a = a.target.result;
    a.objectStoreNames.contains("swpushnotificationsstore") && a.deleteObjectStore("swpushnotificationsstore");
    a.createObjectStore("swpushnotificationsstore", {
        keyPath: "key"
    })
};

function I(a) {
    return new Promise(function(b, c) {
        var f = a.length,
            d = null;
        if (f)
            for (var e = function(a, e) {
                    a || d || (d = e);
                    f--;
                    f || (d ? c(d) : b())
                }, g = u(a), h = g.next(); !h.done; h = g.next()) h.value.then(e.bind(null, !0), e.bind(null, !1));
        else b()
    })
};

function J(a) {
    return G("DeviceId").then(function(b) {
        b = K(null, b, null, a);
        return fetch("/notifications_ajax?action_notification_click=1", {
            credentials: "include",
            method: "POST",
            body: b
        })
    })
}

function N() {
    return Promise.all([G("TimestampLowerBound"), O(), G("DeviceId")]).then(function(a) {
        var b = u(a);
        a = b.next().value;
        var c = b.next().value,
            b = b.next().value;
        if (!a) return Promise.reject(null);
        a = K(c, b, a);
        return fetch("/notifications_ajax?action_get_notifications=1", {
            credentials: "include",
            method: "POST",
            body: a
        }).then(P)
    })
}

function P(a) {
    return a.ok ? a.json().then(Q).catch(function() {}) : Promise.resolve()
}

function Q(a) {
    if (a.errors) return Promise.reject(a.errors);
    a.device_id && E("DeviceId", a.device_id);
    a.ts && E("TimestampLowerBound", a.ts);
    if (a.notifications) {
        var b = [];
        a.notifications.forEach(function(a) {
            b.push(self.registration.showNotification(a.title, {
                body: a.message,
                icon: a.iconUrl,
                data: {
                    nav: a.nav,
                    id: a.id,
                    attributionTag: a.attributionTag
                },
                tag: a.title + a.message + a.iconUrl,
                requireInteraction: !0
            }))
        });
        return I(b)
    }
    return Promise.resolve()
}

function R(a) {
    var b = [S(a), G("RegistrationTimestamp").then(T), U(), V()];
    Promise.all(b).catch(function() {
        return null == a ? W() : Promise.reject()
    }).catch(function() {
        E("IDToken", a);
        X();
        return Promise.resolve()
    })
}

function T(a) {
    a = a || 0;
    return 9E7 >= C() - a ? Promise.resolve() : Promise.reject()
}

function W() {
    return G("DeviceId").then(function(a) {
        return a ? Promise.reject() : Promise.resolve()
    })
}

function S(a) {
    return G("IDToken").then(function(b) {
        return a == b ? Promise.resolve() : Promise.reject()
    })
}

function U() {
    return G("Permission").then(function(a) {
        return Notification.permission == a ? Promise.resolve() : Promise.reject()
    })
}

function V() {
    return G("Endpoint").then(function(a) {
        return O().then(function(b) {
            return a == b ? Promise.resolve() : Promise.reject()
        })
    })
}

function X() {
    E("RegistrationTimestamp", 0);
    O().then(Y).catch(function() {
        Y()
    })
}

function Y(a) {
    a = void 0 === a ? null : a;
    E("Endpoint", a);
    E("Permission", Notification.permission);
    Promise.all([G("DeviceId"), G("NotificationsDisabled")]).then(function(b) {
        var c = u(b);
        b = c.next().value;
        c = c.next().value;
        b = K(a, b, null, null, c);
        fetch("/notifications_ajax?action_register_device=1", {
            credentials: "include",
            method: "POST",
            body: b
        }).then(Z).catch(function() {})
    })
}

function K(a, b, c, f, d) {
    var e = new FormData;
    a && e.append("endpoint", a);
    b && e.append("device_id", b);
    c && e.append("timestamp_lower_bound", c);
    f && (e.append("notification_id", f.id), e.append("attribution_tag", f.attributionTag));
    d && e.append("notifications_disabled", (!!d).toString());
    e.append("permission", Notification.permission);
    return e
}

function Z(a) {
    E("RegistrationTimestamp", C());
    a.ok && a.json().then(function(a) {
        a.ts && E("TimestampLowerBound", a.ts);
        a.device_id && E("DeviceId", a.device_id)
    }).catch(function() {})
}

function O() {
    return self.registration.pushManager.getSubscription().then(function(a) {
        return a ? Promise.resolve(a.endpoint) : Promise.resolve(null)
    })
};
self.oninstall = function(a) {
    a.waitUntil(self.skipWaiting())
};
self.onactivate = function(a) {
    a.waitUntil(self.clients.claim())
};
self.onmessage = function(a) {
    var b = a.data;
    a = b.type;
    b = b.data;
    "notifications_register" == a ? (E("IDToken", b), X()) : "notifications_check_registration" == a && R(b)
};
self.onnotificationclick = function(a) {
    a.notification.close();
    var b = a.notification.data,
        c = self.clients.matchAll({
            type: "window",
            includeUncontrolled: !0
        });
    c.then(function(a) {
        a: {
            var c = b.nav;a = u(a);
            for (var e = a.next(); !e.done; e = a.next())
                if (e = e.value, e.url == c) {
                    e.focus();
                    break a
                }
            self.clients.openWindow(c)
        }
    });
    a.waitUntil(c);
    a.waitUntil(J(b))
};
self.onpush = function(a) {
    a.waitUntil(G("NotificationsDisabled").then(function(a) {
        return a ? Promise.resolve() : N()
    }))
};
self.onpushsubscriptionchange = function() {
    X()
};