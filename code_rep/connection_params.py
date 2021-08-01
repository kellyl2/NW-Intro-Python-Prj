# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 09:52:32 2020

@author: ENLCK
"""
import cred_read as cred
import mygeotab

class connections(object):
    """generates connection details for db connections"""
    
    def __init__(self, source):
        self.source=source
        self.__connect_str=''
                    
    def get_gis_connection(self):
        
        if self.source =="gis_prod":
            self.db_name="gisprod"
            self.__connect_str=str(cred.get_credentials(self.db_name)['u']+'/'+cred.get_credentials(self.db_name)['p']+"@"+self.db_name)
            return self.__connect_str
        
    def get_geotab_connection(self):
        if self.source=='geotab':
            self.db_name="geotab"
            self.__connect_str=mygeotab.API(username=cred.get_credentials(self.db_name)['u'], password=cred.get_credentials(self.db_name)['p'], database="COV_prod")
            return self.__connect_str 