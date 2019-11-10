# -*- coding: utf-8 -*-

'''
/***************************************************************************
 Offline-MapMatching
                                 A QGIS plugin
 desciption of the plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-11-04
        copyright            : (C) 2019 by Christoph Jung
        email                : jagodki.cj@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
'''

__author__ = 'Christoph Jung'
__date__ = '2019-11-04'
__copyright__ = '(C) 2019 by Christoph Jung'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'
from PyQt5.QtCore import QCoreApplication, QUrl
from PyQt5.QtGui import QIcon
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsCoordinateReferenceSystem,
                       QgsProject,
                       QgsProcessingParameterFeatureSink,
                       QgsWkbTypes)
import processing
import time, os.path


class ReduceTrajectoryDensity(QgsProcessingAlgorithm):
    '''
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    '''

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    TRAJECTORY = 'TRAJECTORY'
    DISTANCE = 'DISTANCE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config):
        '''
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        '''
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.TRAJECTORY,
                self.tr('Trajectory layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE,
                self.tr('The minimum distance between to consecutive points'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=100,
                minValue=0.0
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Reduced Trajectory')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        '''
        Here is where the processing itself takes place.
        '''
        start_time = time.time()
        
        #extract all parameters
        trajectory_layer = self.parameterAsVectorLayer(
            parameters,
            self.TRAJECTORY,
            context
        )
        
        distance = self.parameterAsDouble(
            parameters,
            self.DISTANCE,
            context
        )
        
        (output, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            trajectory_layer.fields(),
            QgsWkbTypes.Point,
            trajectory_layer.crs()
        )
        
        #check the inputs
        if trajectory_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.TRAJECTORY))
        
        #present some information to the user
        feedback.pushInfo('CRS of the trajectory is {}'.format(trajectory_layer.sourceCrs().authid()))
        
        #init the progressbar
        feedback.setProgress(0)
        
        #reduce the trajectory density
        result = self.reduceDensity(0, 1, trajectory_layer, distance, output, feedback, trajectory_layer.featureCount())
        
        return {'OUTPUT': dest_id}

    def name(self):
        '''
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        '''
        return 'reduce_trajectory_density'
    
    def helpUrl(self):
        '''
        Returns the URL for the help document, if a help document does exist.
        '''
        dir = os.path.dirname(__file__)
        file = os.path.abspath(os.path.join(dir, '..', 'help_docs', 'help.html'))
        if not os.path.exists(file):
            return ''
        return QUrl.fromLocalFile(file).toString(QUrl.FullyEncoded)

    def shortHelpString(self):
        '''Returns the text for the help widget, if a help document does exist.'''
        dir = os.path.dirname(__file__)
        file = os.path.abspath(os.path.join(dir, '..', 'help_docs', 'help_processing_reduce_density.html'))
        if not os.path.exists(file):
            return ''
        with open(file) as helpf:
            help=helpf.read()
        return help
    
    def displayName(self):
        '''
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        '''
        return self.tr('Reduce Trajectory Density')

    def group(self):
        '''
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        '''
        return self.tr(self.groupId())
    
    def groupId(self):
        '''
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        '''
        return 'Preprocessing'
    
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ReduceTrajectoryDensity()

    def icon(self):
        return QIcon(':/plugins/offline_map_matching/icons/reduce_density_icon.png')
    
    def reduceDensity(self, startIndex, nextIndex, layer, distance, output, feedback, feature_count):
        #handle a pressed cancel button and the progressbar
        feedback.setProgress(int(startIndex / feature_count) * 100)
        if feedback.isCanceled():
            return -99
        
        #init some variables for the following iteration
        start_feature = None
        trajectory_features = layer.getFeatures()
        
        for feature in trajectory_features:
            
            #set the starting feature if none and skip to the next loop
            if start_feature is None:
                start_feature = feature
                output.addFeature(feature)
                continue
                
            #calculate distance, adjust the starting feature after it if distance is big enough
            elif start_feature.geometry().distance(feature.geometry()) >= distance:
                    output.addFeature(feature)
                    start_feature = feature
            
        return -99
        
    
