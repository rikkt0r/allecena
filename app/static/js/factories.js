app.factory('CorrelationsFactory', ['$translate', function($translate) {
    return {
        processRequestForChart: function(correlations) {
            ret = {'labels': [], 'values': []};
            if(correlations) {
                for (var i=0; i< correlations.length; i++) {
                    ret['labels'].push($translate.instant('correlations.' + correlations[i]['name']));
                    ret['values'].push(Math.round(correlations[i]['value']*100));
                }
            }
            
            return ret;
        }
    };
}]);