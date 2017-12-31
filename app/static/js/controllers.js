app.controller('NullCtrl', function ($scope) {});

app.controller('AnalysisCtrl', function ($rootScope, $scope, $routeParams ,$location, $cookies, $uibModal, $translate, poller, HttpService, AnalysisDefaultDataProvider, Flash, HTTP_CONSTANTS) {
    Flash.dismiss();
    
    $scope.analysisOptions = false;
    $scope.submitted = false;
    $scope.data = AnalysisDefaultDataProvider;
    $scope.data.data.account.allegro = '';
    $scope.data.data.account.ebay = '';

    if($cookies.get('session_allegro_id') && $cookies.get('session_allegro_name')) {
        $scope.data.data.account.allegro = $cookies.get('session_allegro_name');
    }

    if($cookies.get('session_ebay_id') && $cookies.get('session_ebay_name')) {
        $scope.data.data.account.ebay = $cookies.get('session_ebay_name');
    }

    if($routeParams["name"]) {
        $scope.data.data.item.name = $routeParams["name"]; 
    }
    
    var transformRequest = function(data) {
        var request = JSON.parse(JSON.stringify(data));
        
        delete request.data.item.category;
        
        if($cookies.get('session_allegro_name')) {
            delete request.data.account.allegro;
        }
        
        if($cookies.get('session_ebay_name')) {
            delete request.data.account.ebay;
        }
        
        if(Object.keys(request.data.account).length == 0) {
            delete request.data.account;
        }
        
        return request;
    }

    $scope.isAllegroUserNeeded = function() {
        if($scope.data.sources.indexOf(HTTP_CONSTANTS.REQUEST.ANALYSIS.SOURCES.ALLEGRO) > -1) {
            return $cookies.get('session_allegro_name') == '';
        }
    }

    $scope.isEbayUserNeeded = function() {
        if($scope.data.sources.indexOf(HTTP_CONSTANTS.REQUEST.ANALYSIS.SOURCES.EBAY) > -1) {
            return $cookies.get('session_ebay_name') == '';
        }
    }

    $scope.send = function(form) {
        $scope.submitted = true;
        
        var index = $scope.data.actions.indexOf('trends');

        if(!$scope.data.data.analysis.advanced && index > -1) {
            $scope.data.actions.splice(index, 1);
        }
        
        var computingCallback = function (httpResult) {            
            if(httpResult.status == 200 && httpResult["data"]["id"]) {
                poller.stopAll()
                $scope.resultId = httpResult["data"]["id"];
                $scope.submitted = false;
                
                $rootScope.newEvent();
            } else if (httpResult.status != 200 && httpResult.status != 204) {
                poller.stopAll()
                $rootScope.httpResult = httpResult;
                $location.path('/error');
            }
        };       
           
        if(form.$valid) {
            var requestData = JSON.stringify(transformRequest($scope.data));
            
            HttpService.sendAnalysisRequest(requestData).then(function (httpResult) {
                    if(httpResult.status == 200 && httpResult["message"]["computingHash"]) {
                        var computingHash =  httpResult["message"]["computingHash"];
                        
                        var analysisPoller = poller.get('/api/computing/polling/', {
                                action: 'post',
                                delay: HTTP_CONSTANTS.ANALYSIS_POLLING_INTERVAL,
                                smart: true,
                                argumentsArray: [
                                    {
                                        computingHash: computingHash  
                                    },
                                    {
                                          headers: {
                                            "X-Auth-Token": $cookies.get('session_token')
                                          }
                                    }
                                ]
                            }
                        );

                        analysisPoller.promise.then(computingCallback, computingCallback, computingCallback);

                    } else {
                        $rootScope.httpResult = httpResult;
                        $location.path('/error');
                    }
            });
        }
    };   
});

app.controller('AnalysisResponseCtrl', function ($rootScope, $scope, $routeParams, $location, $translate, $uibModal, HttpService, CorrelationsFactory) {     
    if($routeParams["id"]) {
        var analyseResultsCallback = function (httpResult) {            
            if(httpResult.status == 200 && httpResult["message"]) {
                var data = httpResult.message;
                $scope.result = data;
                $rootScope.httpResult = undefined;

                if(data.allegro_histogram !== undefined) {
                    $scope.allegro_histogram = {
                        series: [$translate.instant("histogram.legend.current"), $translate.instant("histogram.legend.ended")],
                        labels: data.allegro_histogram.current.prices,
                        data: [
                            data.allegro_histogram.current.counts,
                            data.allegro_histogram.ended.counts
                        ]
                    };
                }

                if(data.allegro_statistics !== undefined) {
                    correlationTmp = CorrelationsFactory.processRequestForChart(data.allegro_statistics.correlations);
                    $scope.allegro_correlations = {
                        labels: correlationTmp['labels'],
                        data: [correlationTmp['values']]
                    };
                }

                if(data.allegro_trends !== undefined) {
                    $scope.allegro_trends = {
                        series: [$translate.instant("trends.legend.mean"), $translate.instant("trends.legend.amount")],
                        labels: data.allegro_trends.dates,
                        data: [
                            data.allegro_trends.meanPrices,
                            data.allegro_trends.amountSold
                        ]
                    }
                }  
            } else {
                $rootScope.httpResult = httpResult;
                $location.path('/error');
            }
        };
        
        $rootScope.sendHttpRequestCallback(HttpService.sendAnalysisResultRequest({'resultId': $routeParams["id"]}), $uibModal, analyseResultsCallback);
    } else {
        $location.path('/analysis'); 
    }
});

app.controller('ErrorCtrl', function ($rootScope, $scope, $location, $translate) { 
    if($rootScope.httpResult) {
        $scope.status = $rootScope.httpResult.status;
        $scope.message = $rootScope.httpResult.message;
        $rootScope.httpResult = undefined;
    } else {
        $location.path('/'); 
    }
    
    $scope.statusModifier = ($scope.status == 401 || $scope.status == 403);

    $scope.getHttpErrorMessage = function() {
        return $translate.instant("http.errors." + $scope.status);
    }
});

app.controller('CategoriesCtrl', function ($scope, $routeParams, $sce, HttpService, $q) {   
    function suggestCategoryRemote(term) {
        if(term.length < 3) {
            return [];
        }

        var deferred = $q.defer();
        var request = HttpService.sendCategoriesRequest(term);
        $scope.categoryRaw = term;

        deferred.resolve(
            request.then(function(response) {
                if(response.status === 200 && response.data) {
                    var results = [];
                    var suggestions = response.data;

                    for (var i = 0; i < suggestions.length && results.length < 10; i++) {
                        var suggestion = suggestions[i],
                            suggestion_label = suggestion.parent_name ? suggestion.parent_name + ' > ' + suggestion.name : suggestion.name;

                        results.push({
                            term: term,
                            value: suggestion_label,
                            tag: suggestion.id,
                            label: suggestion_label
                        });
                    }

                    return results;
                } else {
                    return [];
                }
            })
        );

        return deferred.promise;
    }

    $scope.autocomplete_options = {
        suggest: suggestCategoryRemote,
        on_select: function(data) {
            $scope.data.data.item.category_id = data.tag;
            $scope.data.data.item.category = data.value;
        },
        on_attach: function(data) {
           $scope.category = $scope.categoryRaw;  
        }

    };

    if($routeParams["categoryId"]) { 
        $scope.data.data.item.category_id = $routeParams["categoryId"]; 
        $scope.category_id = $routeParams["categoryId"];
    }
    
    if($routeParams["categoryName"]) { 
        $scope.category = $routeParams["categoryName"]; 
    }

    $scope.category_id = $scope.data.data.item.category_id;
    $scope.category = $scope.data.data.item.category;
});
