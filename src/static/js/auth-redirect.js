(function () {
  const originalFetch = window.fetch.bind(window);

  function isApiRequest(input) {
    if (typeof input === "string") {
      return input.startsWith("/api/");
    }

    if (input instanceof Request) {
      const url = new URL(input.url, window.location.origin);
      return url.pathname.startsWith("/api/");
    }

    return false;
  }

  window.fetch = async function (...args) {
    const response = await originalFetch(...args);

    if (response.status === 401 && isApiRequest(args[0])) {
      window.location.replace("/login");
    }

    return response;
  };
})();