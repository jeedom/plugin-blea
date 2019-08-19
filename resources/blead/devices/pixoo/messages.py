""" Provides Message class to construct messages for the TimeBox """
import logging
class TimeBoxMessages:
    """Support the formation of messages to communicatie with the TimeBox."""

    def checksum(self, payload):
        """Compute the payload checksum. Returned as list with LSM, MSB"""
        logging.debug('Calculate checksum')

        csum = sum(payload)
        lsb = csum & 0b11111111
        msb = csum >> 8
        return [lsb, msb]

    def _extend_with_checksum(self, payload):
        """Extend the payload with two byte with its checksum."""
        logging.debug('Extend with checksum')
        return payload + self.checksum(payload)

    def make_message(self, payload):
        """Make a complete message from the paload data. Add leading 0x01 and
        trailing check sum and 0x02 and escape the payload"""
        cs_payload = self._extend_with_checksum(payload)
        logging.debug('Message built')
        return [0x01] + cs_payload + [0x02]
