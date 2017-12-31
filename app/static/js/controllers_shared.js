app.controller('MenuCtrl', function ($scope, $rootScope, $cookies, $location, $translate) {  
    $scope.events = $rootScope.events;
    $scope.resetEvents = $rootScope.resetEvents;
    
    $rootScope.$watch('events', function() {
       $scope.events = $rootScope.events;
    });
    
    $scope.isActive = function (viewLocation) {
        return viewLocation === $location.path();
    };

    $scope.status = {
        isopen: false
    };
    
    $scope.checkToken = function() {
        if($cookies.get('session_token') && $cookies.get('session_token') != "")
            return true;
        
        return false;
    };
    
    $scope.getToken = function() {
        return $cookies.get('session_token');
    };

    $scope.toggleDropdown = function($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.status.isopen = !$scope.status.isopen;
    };
    
    $scope.setLanguage = function(locale) {
        $translate.use(locale);
    };
});
