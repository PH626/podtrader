from abc import ABCMeta, abstractmethod

from ..events.event import Event


class DataFeedBase(metaclass=ABCMeta):
    """
    DateFeed baae class
    """

    @abstractmethod
    def stream_next(self) -> Event:
        """stream next data event"""
