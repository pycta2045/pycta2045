import abc


class CTA2045Model(abc.ABC):
    @abc.abstractmethod
    def loadup(self,payload):
        pass
    @abc.abstractmethod
    def operating_status(self,payload):
        pass
    @abc.abstractmethod
    def shed(self,payload):
        pass
    @abc.abstractmethod
    def endshed(self,payload):
        pass
    @abc.abstractmethod
    def commodity_read(self,payload):
        pass
    @abc.abstractmethod
    def critical_peak_event(self,payload):
        pass
    @abc.abstractmethod
    def grid_emergency(self,payload):
        pass
