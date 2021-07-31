import abc


class CTA2045Model(abc.ABC):
    @abc.abstractmethod
    def loadup(self):
        pass
    @abc.abstractmethod
    def operating_status(self):
        pass
    @abc.abstractmethod
    def shed(self):
        pass
    @abc.abstractmethod
    def endshed(self):
        pass
    @abc.abstractmethod
    def commodity_read(self,commodity_code):
        pass
