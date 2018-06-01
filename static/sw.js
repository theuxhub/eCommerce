(function () {
  'use strict';
  var urlsToCache = [
    '/static/user/css/style.css',
    'https://fonts.googleapis.com/css?family=Roboto:400,700,300|Material+Icons',
    'https://maxcdn.bootstrapcdn.com/font-awesome/latest/css/font-awesome.min.css',
    'https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js',
    'https://www.googletagmanager.com/gtag/js?id=UA-113254710-1',
    'https://www.google-analytics.com/analytics.js',
  ];

  var CACHE_NAME = 'pages-cache-v89';

  self.addEventListener('install', function (event) {
    // Perform install steps
    event.waitUntil(
      caches.open(CACHE_NAME)
        .then(function (cache) {
          console.log('Opened cache');
          return cache.addAll(urlsToCache);
        })
    );
  });

  self.addEventListener('fetch', function (event) {
    event.respondWith(
      caches.match(event.request)
        .then(function (response) {
          // Cache hit - return response
          if (response) {
            return response;
          }

          // IMPORTANT: Clone the request. A request is a stream and
          // can only be consumed once. Since we are consuming this
          // once by cache and once by the browser for fetch, we need
          // to clone the response.
          var fetchRequest = event.request.clone();

          return fetch(fetchRequest).then(
            function (response) {
              // Check if we received a valid response
              if (!response || response.status !== 200 || response.type !== 'basic') {
                return response;
              }

              // IMPORTANT: Clone the response. A response is a stream
              // and because we want the browser to consume the response
              // as well as the cache consuming the response, we need
              // to clone it so we have two streams.
              var responseToCache = response.clone();

              caches.open(CACHE_NAME)
                .then(function (cache) {
                  cache.put(event.request, responseToCache);
                });

              return response;
            }
          );
        })
    );
  });

})();
