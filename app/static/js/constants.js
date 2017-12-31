app.constant(
   'HTTP_CONSTANTS', {
        'REQUEST': {
            'ANALYSIS': {
                'ACTIONS': {
                    'HINT'       : 'hint',
                    'PREDICTION' : 'prediction',
                    'STATISTICS' : 'statistics',
                    'HISTOGRAM'  : 'histogram',
                    'TRENDS'     : 'trends'
                },
                'SOURCES': {
                    'ALLEGRO'    : 'allegro',
                    'EBAY'       : 'ebay'
                }
            }
        },
        'ANALYSIS_POLLING_INTERVAL' : 5000
   }
);
   
app.constant(   
   'TRIGGERS_CONSTANTS', {
        'CHART_SAMPLES_NUMBER': 20
   }
);
 
