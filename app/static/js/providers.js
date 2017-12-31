app.provider('AnalysisDefaultDataProvider', function(HTTP_CONSTANTS) {
    this.$get = function() {
        return {
            'actions': [
                HTTP_CONSTANTS.REQUEST.ANALYSIS.ACTIONS.HINT,
                HTTP_CONSTANTS.REQUEST.ANALYSIS.ACTIONS.PREDICTION,
                HTTP_CONSTANTS.REQUEST.ANALYSIS.ACTIONS.STATISTICS,
                HTTP_CONSTANTS.REQUEST.ANALYSIS.ACTIONS.HISTOGRAM,
                HTTP_CONSTANTS.REQUEST.ANALYSIS.ACTIONS.TRENDS
            ],
            'sources': [
                HTTP_CONSTANTS.REQUEST.ANALYSIS.SOURCES.ALLEGRO
                //TODO ebay
                //HTTP_CONSTANTS.REQUEST.ANALYSIS.SOURCES.EBAY
            ],
            'data': {
                'item': {
                    'name': '',
                    'guarantee': true,
                    'used': false,
                    'category': '',
                    'category_id': 0,
                    'product_id': 0
                },
                'auction': '',
                'account': {
                    'ebay': '',
                    'allegro':''
                },
                'analysis': {
                    'advanced': true
                },
                'countries': ['poland']
            }
        }
    };
});

app.provider('AddTriggerDefaultDataProvider', function() {
    this.$get = function() {
        return {
            "link": "",
            "provider": "allegro",
            "mode": "price",
            "modeValue" : "",
            "time": "moderate"
        }
    };
});
