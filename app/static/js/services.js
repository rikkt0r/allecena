app.service('HttpService', function($rootScope, $http, $cookies, $location, $q, Flash) {
    return({
        sendAnalysisRequest: sendAnalysisRequest,
        sendAnalysisResultRequest: sendAnalysisResultRequest,
        sendCategoriesRequest: sendCategoriesRequest,
        sendUserAuctionsRequest: sendUserAuctionsRequest,
        sendUserAnalysisRequest: sendUserAnalysisRequest,
        sendUserDataChangeRequest: sendUserDataChangeRequest,
        sendUserTriggersRequest: sendUserTriggersRequest,
        sendUserTriggersAddRequest: sendUserTriggersAddRequest,
        sendUserTriggersDeleteRequest: sendUserTriggersDeleteRequest,
        sendUserTriggersGetRequest: sendUserTriggersGetRequest,
        sendLoginRequest: sendLoginRequest,
        sendLogoutRequest: sendLogoutRequest,
        sendRegisterRequest: sendRegisterRequest,
        sendPasswordResetRequest: sendPasswordResetRequest,
        sendPasswordConfirmResetRequest: sendPasswordConfirmResetRequest,
        sendPasswordChangeRequest: sendPasswordChangeRequest
    });
    
    function sendAnalysisRequest(payload) {
        return(doPost("/api/computing/", payload));
    }

    function sendAnalysisResultRequest(payload) {
        return(doGet("/api/user/results/" + payload["resultId"] + "/", {}));
    }
    
    function sendLoginRequest(payload, facebook) {
        facebook = facebook !== undefined && facebook==true
        return(doPost("/api/user/login/" + (facebook ? "facebook/" : ""), payload));
    }
    
    function sendLogoutRequest(payload, facebook) {
        facebook = facebook !== undefined && facebook==true
        return(doGet("/api/user/logout/" + (facebook ? "facebook/" : ""), payload));
    }

    function sendRegisterRequest(payload) {
        return(doPost("/api/user/register/", payload));
    }

    function sendCategoriesRequest(payload) {
        return(doGet("/api/categories/" + payload, {}, true));
    }

    function sendUserAuctionsRequest() {
        return(doGet("/api/user/auctions/", {}));
    }

    function sendUserAnalysisRequest() {
        return(doGet("/api/user/results/", {}));
    }
    
    function sendUserAnalysisRequest(payload) {
        return(doGet("/api/user/results/", payload));
    }
    
    function sendPasswordResetRequest(payload) {
        return(doPost("/api/user/password/reset/", payload));
    }
    
    function sendPasswordConfirmResetRequest(payload, user, token) {
        return(doPost("/api/user/password/" + user + "/" + token + "/", payload));
    }
    
    function sendPasswordChangeRequest(payload) {
        return(doPost("/api/user/password/", payload));
    }
    
    function sendUserTriggersAddRequest(payload) {
        return(doPost("/api/user/triggers/", payload));
    }
    
    function sendUserTriggersDeleteRequest(triggerId) {
        return(doDelete("/api/user/triggers/" + triggerId + "/", {}));
    }
    
    function sendUserTriggersGetRequest(triggerId) {
        return(doGet("/api/user/triggers/" + triggerId + "/", {}));
    }

    function sendUserDataChangeRequest(payload) {
        return(doPut("/api/user/data/", payload));
    }

    function sendUserTriggersRequest() {
        return(doGet("/api/user/triggers/", {}));
    }
    
    function doPost(url, payload, returnRawRequest) {
        return sendRequest(url, payload, 'post', returnRawRequest);
    }

    function doGet(url, payload, returnRawRequest) {
        return sendRequest(url, payload, 'get', returnRawRequest);
    }

    function doPut(url, payload, returnRawRequest) {
        return sendRequest(url, payload, 'put', returnRawRequest);
    }

    function doDelete(url, payload, returnRawRequest) {
        return sendRequest(url, payload, 'delete', returnRawRequest);
    }

    function sendRequest(url, payload, method, returnRawRequest) {
        var deferred = $q.defer();
        
        var request = $http({
            url         : url,
            dataType    : "json",
            headers: {
                "X-Auth-Token": $cookies.get('session_token')
            },
            contentType : "application/json",
            method      : method,
            data        : payload,
        });

        if(returnRawRequest){
            return request;
        }

        deferred.resolve(request.then(handleSuccess, handleError));

        return deferred.promise;
    }

    function handleError(response) {
        var message = 'Wystąpił nieoczekiwany błąd.';

        switch(response.status) {
            case 401:
                message = 'Twoja sesja wygasła. Zaloguj się ponownie.';
                $cookies.remove('session_token');
                break;
            case 403:
                message = 'Brak uprawnień. Zaloguj się.';
                break;
            case 409:
                message = 'Nie można wykonać operacji - żądany zasób już istnieje.';
                break;
            case 501:
                message = 'Przepraszamy! Funkcjonalność w trakcie implementacji.';

            default:
                break;
        }

        return({
            "successfull" : false,
            "status"      : response.status,
            "message"     : message
        });
    }

    function handleSuccess(response) {                
        return({
            "successfull" : true,
            "status"      : response.status,
            "message"     : response.data
        });
    }
});