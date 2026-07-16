// Attaches the login JWT to every same-origin /api request so individual
// pages don't need to manage Authorization headers themselves.
(function () {
    const originalFetch = window.fetch;
    window.fetch = function (input, init) {
        const url = typeof input === "string" ? input : input.url;
        if (url && url.startsWith("/api/")) {
            const token = localStorage.getItem("accessToken");
            if (token) {
                init = init || {};
                init.headers = new Headers(init.headers || {});
                if (!init.headers.has("Authorization")) {
                    init.headers.set("Authorization", "Bearer " + token);
                }
            }
        }
        return originalFetch.call(this, input, init);
    };

    window.logout = function () {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("userName");
        localStorage.removeItem("userRole");
        window.location.href = "/login";
    };
})();
