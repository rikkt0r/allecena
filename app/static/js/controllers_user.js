app.controller('UserLoginCtrl', function ($scope, $rootScope, $window, $cookies, $location, $translate, $uibModal, HttpService, Facebook) {
    $scope.submitted = false;

    $scope.data = {
        'email' : '',
        'password' : ''
    };
    
    $scope.login = function(form) {
        $scope.submitted = true;
        
        var loginRequestCallback = function (httpResult) {
            if(httpResult.status == 200) {
                var now = new Date();
                var expireDate = new Date(now.getFullYear(), now.getMonth(), now.getDay()+1);
                
                $cookies.put('session_token', httpResult["message"]["token"], {expired: expireDate});
                
                if (httpResult["message"]["accounts"]) {
                    $cookies.put('session_allegro_id',       httpResult["message"]["accounts"]["allegro"]["id"],    {expired: expireDate});
                    $cookies.put('session_allegro_name',     httpResult["message"]["accounts"]["allegro"]["name"],  {expired: expireDate});
                    $cookies.put('session_ebay_id',          httpResult["message"]["accounts"]["ebay"]["id"],       {expired: expireDate});
                    $cookies.put('session_ebay_name',        httpResult["message"]["accounts"]["ebay"]["name"],     {expired: expireDate});
                }
                
                if (httpResult["message"]["user"]) {
                    $cookies.put('session_user_firstname',   httpResult["message"]["user"]["first_name"],           {expired: expireDate});
                    $cookies.put('session_user_lastname',    httpResult["message"]["user"]["last_name"],            {expired: expireDate});
                }
                
                $location.path("/user");
            } else if (httpResult.status == 401) {
                $scope.submitted = false;
                form.email.$setValidity("invalidUser", false);
                form.password.$setValidity("invalidUser", false);
            } else {
                $rootScope.httpResult = httpResult;
                $location.path('/error');
            }
        }
         
        if(form.$valid) {
            var loginRequestData = JSON.stringify({
                'username'  : $scope.data.email,
                'password'  : $rootScope.hashPassword($scope.data.password)
            });
           
            $rootScope.sendHttpRequestCallback(HttpService.sendLoginRequest(loginRequestData), $uibModal, loginRequestCallback);
        }
    }
    
    function facebookCheckStatus() {
        return Facebook.getLoginStatus(function(response) {});
    };

    function facebookAccount() {
      return Facebook.api('/me?fields=email', function(response) {});
    }
    
    $scope.facebookLogin = function() {       
        Facebook.login(function(response) {
            if(response.status === "connected" && response.authResponse.accessToken) {
                var facebookToken = response.authResponse.accessToken;
                
                var loginRequestCallback = function (httpResult) {
                    if(httpResult.status == 200) {
                        var now = new Date();
                        var expireDate = new Date(now.getFullYear(), now.getMonth(), now.getDay()+1);
                        
                        $cookies.put('session_token', httpResult["message"]["token"], {expired: expireDate});
                        $cookies.put('session_facebook', true, {expired: expireDate});
                        
                        if (httpResult["message"]["accounts"]) {
                            $cookies.put('session_allegro_id',       httpResult["message"]["accounts"]["allegro"]["id"],    {expired: expireDate});
                            $cookies.put('session_allegro_name',     httpResult["message"]["accounts"]["allegro"]["name"],  {expired: expireDate});
                            $cookies.put('session_ebay_id',          httpResult["message"]["accounts"]["ebay"]["id"],       {expired: expireDate});
                            $cookies.put('session_ebay_name',        httpResult["message"]["accounts"]["ebay"]["name"],     {expired: expireDate});
                        }
                        
                        if (httpResult["message"]["user"]) {
                            $cookies.put('session_user_firstname',   httpResult["message"]["user"]["first_name"],           {expired: expireDate});
                            $cookies.put('session_user_lastname',    httpResult["message"]["user"]["last_name"],            {expired: expireDate});
                        }
                        
                        $location.path('/user');
                    } else {
                        $rootScope.httpResult = httpResult;
                        $location.path('/error');
                    }
                }
                
                facebookAccount().then(function(response){
                    if(response && response['email']) {                           
                        var loginRequestData = JSON.stringify({
                            'username'     : response['email'],
                            'password'     : facebookToken
                        });
                        
                        $rootScope.sendHttpRequestCallback(HttpService.sendLoginRequest(loginRequestData, true), $uibModal, loginRequestCallback);
                    } else {
                        $location.path('/error');
                    }
                });
            }
        });
    }
    
    function sendLoginRequest(callback) {
        var requestData = JSON.stringify({
                'login'     : $scope.data.email,
                'password'  : $rootScope.hashPassword($scope.data.password),
            });
           
        $rootScope.sendHttpRequestCallback(HttpService.sendLoginRequest(requestData), $uibModal, callback);
    }
    
    $scope.resetPassword = function() {
        $location.path('/user/password/reset');
    }
});
        
app.controller('UserLogoutCtrl', function ($scope, $rootScope, $cookies, $location, $uibModal, HttpService, Facebook) {   
    var httpCallback = function (httpResult) {
        if(httpResult.status == 200) {
            var facebookSession = $cookies.get('session_facebook');
            var redirect = function() {
                $cookies.put('session_token','')
                $cookies.remove('session_facebook');
                $cookies.put('session_allegro_id', '');
                $cookies.put('session_allegro_name', '');
                $cookies.put('session_ebay_id', '');
                $cookies.put('session_ebay_name', '');
                $cookies.put('session_user_firstname', '');
                $cookies.put('session_user_lastname', '');
                $location.path("/");
            }
            
            if(facebookSession) {
                Facebook.logout(function(response) {
                   redirect();
                })
            } else {
                redirect();
            }
        } else {
            $location.path('/error');
        }
    }
         
    var requestData = JSON.stringify({
        'token': $cookies.get('session_token')
    });
        
    $rootScope.sendHttpRequestCallback(HttpService.sendLogoutRequest(requestData, $cookies.get('session_facebook')), $uibModal, httpCallback);
});

app.controller('UserRegisterCtrl', function ($scope, $rootScope, $cookies, $location, $translate, $uibModal, HttpService) {
    $scope.submitted = false;

    $scope.data = {
        'email' : '',
        'password' : '',
        'password_repeat' : '',
    };

    $scope.register = function(form) {
        $scope.submitted = true;

        var httpCallback = function (httpResult) {
            if(httpResult.status == 200) {
                var now = new Date();
                var expireDate = new Date(now.getFullYear(), now.getMonth(), now.getDay()+1);
                $cookies.put('session_token', httpResult["message"]["token"], {expired: expireDate});
                $location.path("/user/register/successful");
            } else if (httpResult.status == 409) {
                $scope.submitted = false;
                form.email.$setValidity("invalidUser", false);
                form.password.$setValidity("invalidUser", false);
            } else {
                $rootScope.httpResult = httpResult;
                $location.path('/error');
            }
        }
        form.password.$setValidity("passwordMatch", true);
        if($scope.data.password !== $scope.data.password_repeat) {
            form.password.$setValidity("passwordMatch", false);
        } else if(form.$valid) {
            var requestData = JSON.stringify({
                'email'     : $scope.data.email,
                'new_password'  : $rootScope.hashPassword($scope.data.password),
                'new_password_repeat'  : $rootScope.hashPassword($scope.data.password_repeat)
            });

            $rootScope.sendHttpRequestCallback(HttpService.sendRegisterRequest(requestData), $uibModal, httpCallback);
        }
    }
});

app.controller('UserPasswordResetCtrl', function ($scope, $rootScope, $location, $uibModal, HttpService) {
     $scope.submitted = false;
    
     $scope.resetPassword = function(form) {   
        $scope.submitted = true;
        
        if(form.$valid) {
            var requestData = JSON.stringify({
                'email'  : $scope.data.email
            });
           
            $rootScope.sendHttpRequest($location, HttpService.sendPasswordResetRequest(requestData), $uibModal, '/user/password/reset/successful');
        }
     }
});

app.controller('UserPasswordChangeCtrl', function ($scope, $rootScope, $routeParams, $location, $translate, $uibModal, HttpService, Flash) {
    $scope.submitted = false;

    $scope.data = {
        'password' : '',
        'password_repeat' : '',
    };
    
    $scope.changePassword = function(form) {
        $scope.submitted = true;

        var httpCallback = function (httpResult) {
            if(httpResult.status == 200) {
                Flash.create('success', $translate.instant('messages.success'), 'custom-class');
            } else {
                $rootScope.httpResult = httpResult;
                $location.path('/error');
            }
        }

        form.password.$setValidity("passwordMatch", true);
        if($scope.data.password !== $scope.data.password_repeat) {
            form.password.$setValidity("passwordMatch", false);
        } else if(form.$valid) {
            var requestData = JSON.stringify({
                'new_password'  : $rootScope.hashPassword($scope.data.password),
                'new_password_repeat'  : $rootScope.hashPassword($scope.data.password_repeat)
            });

            if($routeParams["user"] && $routeParams["token"]) {
                $rootScope.sendHttpRequestCallback(HttpService.sendPasswordConfirmResetRequest(requestData, $routeParams["user"], $routeParams["token"]), $uibModal, httpCallback);
            } else {
                $rootScope.sendHttpRequestCallback(HttpService.sendPasswordChangeRequest(requestData), $uibModal, httpCallback);
            }
        }
    };
});

app.controller('UserRegisteredCtrl', function ($scope, $location, $routeParams) {});

app.controller('UserPanelCtrl', function ($scope, $location, $routeParams) {
    $scope.showSettings = function () {
        $location.path('/user/settings');
    }

    $scope.showAnalysisResults = function () {
        $location.path('/user/results');
    }
    
    $scope.showAnalysis = function () {
        $location.path('/analysis');
    }
    
    $scope.showAuctions = function () {
        $location.path('/user/auctions');
    }
    
    $scope.showTriggersResults = function () {
        $location.path('/user/triggers');
    }
    
    $scope.showTriggers = function () {
        $location.path('/user/triggers');
    }
});

app.controller('UserSettingsCtrl', function ($scope, $rootScope, $cookies, $location, $translate, $uibModal, HttpService, Flash) {
    $scope.submitted = false;

    $scope.data = {
        'firstname'     : $cookies.get('session_user_firstname'),
        'lastname'      : $cookies.get('session_user_lastname'),
        'allegro_login' : $cookies.get('session_allegro_name'),
        'ebay_login'    : $cookies.get('session_ebay_name')
    };
    
    $scope.changeUserData = function(form) {
        $scope.submitted = true;

        var httpCallback = function (httpResult) {
            if(httpResult.status == 200) {
                Flash.create('success', $translate.instant('messages.success'), 'custom-class');
            } else {
                $rootScope.httpResult = httpResult;
                $location.path('/error');
            }
        }

        var requestData = JSON.stringify({
            'first_name'    : $scope.data.firstname,
            'last_name'     : $scope.data.lastname,
            'allegro_login' : $scope.data.allegro_login,
            'ebay_login'    : $scope.data.ebay_login
        });

        $rootScope.sendHttpRequestCallback(HttpService.sendUserDataChangeRequest(requestData), $uibModal, httpCallback);
    }
});

app.controller('UserTriggerListCtrl', function ($scope, $rootScope, $location, $translate, $uibModal, HttpService, Flash, AddTriggerDefaultDataProvider) {
    $scope.submitted = false;
    $scope.data = AddTriggerDefaultDataProvider;

    var parseAllegroLink = function(auctionLinkValue){
        var auctionLinkValueSplited = auctionLinkValue.split('-');
        return auctionLinkValueSplited[auctionLinkValueSplited.length-1].split('.html')[0].split('i')[1];
    }        

    var getTriggers = function(){
        var callback = function(httpResult) {
            if(httpResult.status == 200 && httpResult["message"]["triggers"]) {
                $scope.triggers = httpResult["message"]["triggers"];
            } else {
                $rootScope.httpResult = httpResult;
                $location.path('/error');
            }
        }

        $rootScope.sendHttpRequestCallback(
            HttpService.sendUserTriggersRequest(),
            $uibModal,
            callback
        );
    }

    if(!$scope.triggers) {
        getTriggers();
    }

    $scope.send = function(form) {        
        $scope.submitted = true;

        if($scope.data.auctionLink && form.$valid) {
            var auctionId = parseAllegroLink($scope.data.auctionLink);
            
            var requestData = {
                "auction_id": auctionId,
                "provider": $scope.data.provider,
                "mode": $scope.data.mode,
                "mode_value" : $scope.data.modeValue,
                "time": $scope.data.time
            }
            
            var httpCallback = function (httpResult) {
                if(httpResult.status == 201) {
                    getTriggers();
                    Flash.create('success', $translate.instant('messages.success'), 'custom-class');
                    $scope.showDetails(httpResult.message.triggerId)
                } else {
                    $rootScope.httpResult = httpResult;
                    $location.path('/error');
                }
            }
   
            $rootScope.sendHttpRequestCallback(HttpService.sendUserTriggersAddRequest(requestData), $uibModal, httpCallback);
        }
    }
    

    $scope.showDetails = function(triggerId) {
        $location.path("/user/triggers/" + triggerId);
    }
    
    $scope.delete = function(triggerId) {
        var httpCallback = function (httpResult) {
            if(httpResult.status == 200) {
                getTriggers();
                Flash.create('success', $translate.instant('messages.success'), 'custom-class');
            } else {
                $rootScope.httpResult = httpResult;
                $location.path('/error');
            }
        }
   
        $rootScope.sendHttpRequestCallback(HttpService.sendUserTriggersDeleteRequest(triggerId), $uibModal, httpCallback);
    }
});

app.controller('UserTriggerDetailsCtrl', function ($scope, $rootScope, $routeParams, $location, $translate, $uibModal, HttpService, TRIGGERS_CONSTANTS) {
    if($routeParams["triggerId"]) {
        $scope.triggerId = $routeParams["triggerId"];        
        
        var httpCallback = function (httpResult) {
            if(httpResult.status == 200  && !httpResult["message"]["error"]) {

                var data = httpResult["message"];
                $scope.trigger = data;

                var times = [];
                var values = [];
                var number = data.data.length;
                var interval = Math.floor(number / TRIGGERS_CONSTANTS.CHART_SAMPLES_NUMBER);
                
                if(interval === 0) {
                    interval = 1;
                }
                
                for(var i=0; i < number; i = i + interval) {
                    times.push(data.data[i].time);
                    values.push(data.data[i].value);
                }

                if(values.length > 0) {

                    $scope.trigger_chart = {
                        series: [$translate.instant("user.triggers.legend.price"),],
                        labels: times,
                        data: [values]
                    };
                }

            } else {
                $rootScope.httpResult = httpResult;
                $location.path('/error');
            }
        }
        
        $rootScope.sendHttpRequestCallback(HttpService.sendUserTriggersGetRequest($scope.triggerId), $uibModal, httpCallback);
    } else {
        $location.path('/error');
    }
    
    $scope.translateMode = function(mode) {
        return $translate.instant('enumerations.triggersMode.' + mode);
    }
    
    $scope.translateTime = function(time) {
        return $translate.instant('enumerations.triggersTime.' + time);
    }
    
});

app.controller('UserResultListCtrl', function ($scope, $rootScope, $location, $translate, HttpService) {   
    HttpService.sendUserAnalysisRequest().then(function(httpResult) {
        if(httpResult.status == 200 && httpResult["message"]) {
            $scope.results = httpResult["message"];
        } else {
            $rootScope.httpResult = httpResult;
            $location.path('/error');
        }  
    });
});

app.controller('UserAuctionListCtrl', function ($scope, $rootScope, $location, $translate, $uibModal, HttpService) {
    var callback = function(httpResult) {
        if(httpResult.status == 200) {
            $scope.auctions = httpResult["message"]["userAuctions"] || [];
        } else {
            $rootScope.httpResult = httpResult;
            $location.path('/error');
        }
    }
    
    if(!$scope.auctions) {
        $rootScope.sendHttpRequestCallback(
            HttpService.sendUserAuctionsRequest(),
            $uibModal,
            callback
        );
    }
       
    $scope.showDetails = function(auction) {
        $location.path("/analysis/" + auction.name + "/" + auction.categoryId + "/" + auction.categoryName);
    }
});