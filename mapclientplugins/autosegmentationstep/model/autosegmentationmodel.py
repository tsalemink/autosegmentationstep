"""
Created: April, 2023

@author: tsalemink
"""
from opencmiss.zinc.context import Context


class AutoSegmentationModel(object):
    def __init__(self, input_image_data):
        self._context = Context('Auto-Segmentation')

    def get_context(self):
        return self._context
