from collections import namedtuple
from datetime import datetime, time
import pandas as pd
import random
import re
from typing import Dict, List, IO

from .logger import logger

TalkInfo = namedtuple("TalkInfo", ["conference_talk", "duration"])

SCHEDULE_TYPE = Dict[int, TalkInfo]
MULTIPLE_SCHEDULE_TYPE = List[Dict[int, TalkInfo]]

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
        self.conference_data = {}

    @staticmethod
    def _extract_talk_duration(row):
        if "lightning" in row:
            return dict(conference_talk=row, duration=5)
        
        pattern = re.compile(r'^(.*?)\s*(\d+)\s*(min|min\s*min|mins)?$')
        match = pattern.match(row)
        if match:
            talk = match.group(1).strip()
            duration = int(match.group(2))
            return dict(conference_talk=talk, duration= duration)
        return dict(conference_talk=row, duration=0)

    @staticmethod
    def _format_track_output(counter: int, schedules: SCHEDULE_TYPE) -> Dict[str, list]:
        sessions = []
        for time, talk_info in schedules.items():
            hours, minutes = divmod(time, 60)
            dt_time = datetime(2024, 1, 2, hours, minutes)
            duration_mins = f"[{talk_info.duration} mins]" if talk_info.duration else ""
            sessions.append(dict(time=f"{dt_time.strftime('%I:%M %p')}", talk=f"{talk_info.conference_talk} {duration_mins}"))
        tracks = {f"Track {counter}": sessions}
        return tracks
    
    def _create_schedule(self, start_time: int, end_time: int) -> SCHEDULE_TYPE:
        schedule = {}
        current_time = start_time
        used_talks = set()
        while current_time < end_time:
            available_talks = [
                talk_id
                for talk_id, talk_info in self.conference_data.items()
                if talk_id not in used_talks and talk_info["duration"] <= (end_time - current_time)
            ]

            if not available_talks:
                break
            
            selected_talk_id = random.choice(available_talks)
            selected_talk_info = self.conference_data[selected_talk_id]
            schedule[current_time] = TalkInfo(selected_talk_info["conference_talk"], selected_talk_info["duration"])
            used_talks.add(selected_talk_id)
            self.conference_data.pop(selected_talk_id)
            current_time += selected_talk_info["duration"]

        return schedule
    
    def _create_morning_schedule(self) -> SCHEDULE_TYPE:
        return self._create_schedule(self.MORNING_START_TIME, self.MORNING_END_TIME)
    
    def _create_afternoon_schedule(self) -> SCHEDULE_TYPE:
        return self._create_schedule(self.AFTERNOON_START_TIME, self.AFTERNOON_END_TIME)
    
    def _create_lunch_schedule(self) -> SCHEDULE_TYPE:
        schedule = {self.LUNCH_START_TIME: TalkInfo(self.LUNCH, self.LUNCH_END_TIME - self.LUNCH_START_TIME)}
        return schedule
    
    def _create_networking_schedule(self, current_schedule: SCHEDULE_TYPE) -> SCHEDULE_TYPE:
        last_key, last_value = max(current_schedule.items())
        networking_start_time = max(last_key + last_value.duration, 16 * 60)
        schedule = {networking_start_time: TalkInfo(self.NETWORK_EVENT, 0)}
        return schedule

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

    def create_multiple_schedules(self) -> MULTIPLE_SCHEDULE_TYPE:
        all_schedules = []
        counter = 1
        while self.conference_data:
            morning_section = self._create_morning_schedule()
            lunch_section = self._create_lunch_schedule()
            afternoon_section = self._create_afternoon_schedule()
            current_schedule = {**morning_section, **lunch_section, **afternoon_section}
            networking_section = self._create_networking_schedule(current_schedule)
            current_schedule.update(networking_section)
            tracks = self._format_track_output(counter, current_schedule)
            all_schedules.append(tracks)
            counter+=1
        return all_schedules