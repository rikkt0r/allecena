var app = angular.module('AlleCena', [
  'ngRoute',
  'ngCookies',
  'ngSanitize',
  'ui.bootstrap',
  'pascalprecht.translate',
  'chart.js',
  'flash',
  'checklist-model',
  'MassAutoComplete',
  'emguo.poller',
  'facebook'
]).config(['$routeProvider', '$httpProvider',
  function($routeProvider, $httpProvider) {
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    $routeProvider.
        when('/', {templateUrl: '/static/templates/pages/home.html',controller: 'NullCtrl'}).
        when('/error', {templateUrl: '/static/templates/pages/error.html',controller: 'ErrorCtrl'}).
        when('/analysis', {templateUrl: '/static/templates/pages/analysis/request.html', controller: 'AnalysisCtrl'}).
        when('/analysis/:name/:categoryId/:categoryName', {templateUrl: '/static/templates/pages/analysis/request.html', controller: 'AnalysisCtrl'}).
        when('/analysis/result/:id', {templateUrl: '/static/templates/pages/analysis/response.html', controller: 'AnalysisResponseCtrl'}).
        when('/about', {templateUrl: '/static/templates/pages/about.html', controller: 'NullCtrl'}).
        when('/user', {templateUrl: '/static/templates/pages/user/panel.html',controller: 'UserPanelCtrl'}).
        when('/user/settings', {templateUrl: '/static/templates/pages/user/settings.html',controller: 'UserSettingsCtrl'}).
        when('/user/login', {templateUrl: '/static/templates/pages/user/login.html',controller: 'UserLoginCtrl'}).
        when('/user/logout', {templateUrl: '/static/templates/pages/user/logout.html',controller: 'UserLogoutCtrl'}).
        when('/user/register', {templateUrl: '/static/templates/pages/user/register.html',controller: 'UserRegisterCtrl'}).
        when('/user/register/successful', {templateUrl: '/static/templates/pages/user/registered.html',controller: 'UserRegisteredCtrl'}).
        when('/user/password/reset', {templateUrl: '/static/templates/pages/user/password_reset.html',controller: 'UserPasswordResetCtrl'}).
        when('/user/password/reset/:user/:token', {templateUrl: '/static/templates/pages/user/password_change.html',controller: 'UserPasswordChangeCtrl'}).
        when('/user/password/reset/successful', {templateUrl: '/static/templates/pages/user/password_reset_result.html',controller: 'NullCtrl'}).
        when('/user/triggers', {templateUrl: '/static/templates/pages/user/triggers.html',controller: 'UserTriggerListCtrl'}).
        when('/user/triggers/:triggerId', {templateUrl: '/static/templates/pages/user/trigger_details.html',controller: 'UserTriggerDetailsCtrl'}).
        when('/user/results', {templateUrl: '/static/templates/pages/user/results.html',controller: 'UserResultListCtrl'}).
        when('/user/auctions', {templateUrl: '/static/templates/pages/user/auctions.html',controller: 'UserAuctionListCtrl'}).
        otherwise({redirectTo: '/'});
    }]
).config(['$translateProvider', function($translateProvider) {
        $translateProvider.useStaticFilesLoader({
            prefix: 'static/translations/',
            suffix: '.json'
        });
        
        $translateProvider.determinePreferredLanguage()
                          .preferredLanguage('pl_PL')
                          .fallbackLanguage(['pl_PL']);
    }]  
).config(['FacebookProvider', function(FacebookProvider) {
     FacebookProvider.init(639725602835286);
  }] 
).run(['$rootScope', '$cookies', function($rootScope, $cookies) {
    if(!$cookies.get('session_token')) {
        $cookies.put('session_token','');
    }
    
    if(!$cookies.get('session_allegro_id')) {
        $cookies.put('session_allegro_id','');
    }
    
    if(!$cookies.get('session_allegro_name')) {
        $cookies.put('session_allegro_name','');
    }
    
    if(!$cookies.get('session_ebay_id')) {
        $cookies.put('session_ebay_id','');
    }
    
    if(!$cookies.get('session_ebay_name')) {
        $cookies.put('session_ebay_name','');
    }

    if(!$cookies.get('session_user_firstname')) {
        $cookies.put('session_user_firstname','');
    }

    if(!$cookies.get('session_user_lastname')) {
        $cookies.put('session_user_lastname','');
    }
  
    if(!$cookies.get('events')) {
        $cookies.put('events', 0);
    }
    
    $rootScope.events = $cookies.get('events');
    
    $rootScope.newEvent = function() {
        $rootScope.events++;
        $cookies.put('events', $rootScope.events);
    }
    
    $rootScope.resetEvents = function() {
        $rootScope.events = 0;
        $cookies.put('events', 0);
    }

    $rootScope.startWaiting = function ($uibModal) {        
        this.modalInstance = $uibModal.open({
            animation: true,
            templateUrl: '/static/templates/pages/common/wait.html',
            controller: 'NullCtrl',
            keyboard: false,
        });

        return this.modalInstance.rendered;
    }
    
    $rootScope.stopWaiting = function () {
        this.modalInstance.dismiss('cancel');
    }
    
    $rootScope.sendHttpRequest = function ($location, fn, $uibModal, path) {
        var callback = function (data) {
            $rootScope.httpResult = data;
                    
            if($rootScope.httpResult == null || $rootScope.httpResult.message == null || $rootScope.httpResult.message.error) {
                $location.path('/error');  
            } else {
                $location.path(path);
            }
        }
        
        $rootScope.sendHttpRequestCallback(fn, $uibModal, callback);
    }
    
    $rootScope.sendHttpRequestCallback = function (fn, $uibModal, callback) {
        $rootScope.startWaiting($uibModal).then(function() {
            fn.then(
                function(data) {
                    $rootScope.stopWaiting();                    
                    callback(data);
                }
            );
        });
    }
    
    $rootScope.hashPassword = function(plainTextPassword) {
        return btoa(unescape(encodeURIComponent(plainTextPassword)));
    }
}]);