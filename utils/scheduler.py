from datetime import datetime
import pandas as pd
import random
import re
from typing import Dict, List, IO
from pydantic import BaseModel

from .logger import logger

class TalkInfo(BaseModel):
    conference_talk: str
    duration: int


class TrackInfo(BaseModel):
    time: str
    talk: str


SESSION = Dict[int, TalkInfo]
TRACK = Dict[str, TrackInfo]
TRACKS = List[TRACK]

class SchedulingError(Exception):
  """Base class for exceptions in scheduling"""

  def __init__(self, message):
    self.message = message

  def __str__(self):
    return f'Scheduling Error: {self.message}'
  

class Scheduler:

    MORNING_START_TIME = 9 * 60 
    MORNING_END_TIME = 12 * 60 
    LUNCH_START_TIME =12 * 60 
    LUNCH_END_TIME = 13 * 60 
    AFTERNOON_START_TIME = 13 * 60 
    AFTERNOON_END_TIME = 17 * 60 

    LUNCH = 'Lunch'
    NETWORK_EVENT = 'Networking event'

    
    def __init__(self) -> None:
        self.conference_data: Dict[int, TalkInfo] = {}

    @staticmethod
    def _extract_talk_duration(row) -> TalkInfo:
        if "lightning" in row:
            return TalkInfo(conference_talk=row, duration=5)
        
        pattern = re.compile(r'^(.*?)\s*(\d+)\s*(min|min\s*min|mins)?$')
        match = pattern.match(row)
        if match:
            talk = match.group(1).strip()
            duration = int(match.group(2))
            return TalkInfo(conference_talk=talk, duration= duration)
        return TalkInfo(conference_talk=row, duration=0)

    @staticmethod
    def _format_track_output(counter: int, daily_sessions: SESSION) -> TRACK:
        formated_daily_sessions = []
        for time, talk_info in daily_sessions.items():
            hours, minutes = divmod(time, 60)
            dt_time = datetime(2024, 1, 2, hours, minutes)
            duration_mins = f"[{talk_info.duration} mins]" if talk_info.duration else ""
            formated_daily_sessions.append(TrackInfo(time=f"{dt_time.strftime('%I:%M %p')}", talk=f"{talk_info.conference_talk} {duration_mins}"))
        track = {f"Track {counter}": formated_daily_sessions}
        return track
    
    def _create_session(self, start_time: int, end_time: int) -> SESSION:
        session = {}
        current_time = start_time
        used_talks = set()
        while current_time < end_time:
            available_talks = [
                talk_id
                for talk_id, talk_info in self.conference_data.items()
                if talk_id not in used_talks and talk_info.duration <= (end_time - current_time)
            ]

            if not available_talks:
                break
            
            selected_talk_id = random.choice(available_talks)
            selected_talk_info = self.conference_data[selected_talk_id]
            session[current_time] = TalkInfo(conference_talk=selected_talk_info.conference_talk, duration=selected_talk_info.duration)
            used_talks.add(selected_talk_id)
            self.conference_data.pop(selected_talk_id)
            current_time += selected_talk_info.duration

        return session
    
    def _create_morning_session(self) -> SESSION:
        return self._create_session(self.MORNING_START_TIME, self.MORNING_END_TIME)
    
    def _create_afternoon_session(self) -> SESSION:
        return self._create_session(self.AFTERNOON_START_TIME, self.AFTERNOON_END_TIME)
    
    def _create_lunch_session(self) -> SESSION:
        session = {self.LUNCH_START_TIME: TalkInfo(conference_talk=self.LUNCH, duration=self.LUNCH_END_TIME - self.LUNCH_START_TIME)}
        return session
    
    def _create_networking_session(self, current_schedule: SESSION) -> SESSION:
        last_key, last_value = max(current_schedule.items())
        networking_start_time = max(last_key + last_value.duration, 16 * 60)
        session = {networking_start_time: TalkInfo(conference_talk=self.NETWORK_EVENT, duration=0)}
        return session

    def clean_data(self, file_byte: IO[bytes]):
        try:
            df = pd.read_csv(file_byte, header=None, names=['talk'])
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise SchedulingError(f"Invalid CSV file. Please upload a valid one or Contact support.")
        
        if df.empty:
            raise SchedulingError("Empty CSV file. Please upload a valid one.")
        
        df['talk_dict'] = df['talk'].apply(self._extract_talk_duration)
        result_dict = df['talk_dict'].to_dict()
        self.conference_data = result_dict

    def create_tracks(self) -> TRACKS:
        tracks = []
        counter = 1
        while self.conference_data:
            morning_session = self._create_morning_session()
            lunch_session = self._create_lunch_session()
            afternoon_session = self._create_afternoon_session()
            daily_sessions = {**morning_session, **lunch_session, **afternoon_session}
            networking_session = self._create_networking_session(daily_sessions)
            daily_sessions.update(networking_session)
            track = self._format_track_output(counter, daily_sessions)
            tracks.append(track)
            counter+=1
        return tracks