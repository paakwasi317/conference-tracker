from collections import namedtuple
import pandas as pd
import random
import re
from typing import Dict, List

TalkInfo = namedtuple("TalkInfo", ["conference_talk", "duration"])

SCHEDULE_TYPE = Dict[int, TalkInfo]
MULTIPLE_SCHEDULE_TYPE = List[Dict[int, TalkInfo]]

class Scheduler:

    MORNING_START_TIME = 9 * 60 
    MORNING_END_TIME = 12 * 60 
    LUNCH_START_TIME =12 * 60 
    LUNCH_END_TIME = 13 * 60 
    AFTERNOON_START_TIME = 13 * 60 
    AFTERNOON_END_TIME = 17 * 60 

    LUNCH = 'Lunch'
    NETWORK_EVENT = 'networking_event'

    
    def __init__(self) -> None:
        self.conference_data = []

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
    
    def _create_networking_schedule(self, afternoon_section: SCHEDULE_TYPE) -> SCHEDULE_TYPE:
        last_key, last_value = max(afternoon_section.items())
        networking_start_time = max(last_key + last_value.duration, 16 * 60)
        schedule = {networking_start_time: TalkInfo(self.NETWORK_EVENT, 0)}
        return schedule

    def clean_data(self):
        df = pd.read_csv('activities.csv', header=None, names=['talk'])
        df['talk_dict'] = df['talk'].apply(self._extract_talk_duration)
        result_dict = df['talk_dict'].to_dict()
        self.conference_data = result_dict

    def create_multiple_schedules(self) -> MULTIPLE_SCHEDULE_TYPE:
        all_schedules = []
        while self.conference_data:
            morning_section = self._create_morning_schedule()
            lunch_section = self._create_lunch_schedule()
            afternoon_section = self._create_afternoon_schedule()
            networking_section = self._create_networking_schedule(afternoon_section)
            current_schedule = {**morning_section, **lunch_section, **afternoon_section, **networking_section}
            all_schedules.append(current_schedule)
        return all_schedules


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.clean_data()
    all_schedules_result = scheduler.create_multiple_schedules()
    print(all_schedules_result)

    for idx, schedule_result in enumerate(all_schedules_result):
        print(f"Track {idx + 1}:")
        for time, talk_info in schedule_result.items():
            end_time = time + talk_info.duration
            print(f"{time // 60:02d}:{time % 60:02d} {talk_info.conference_talk} {talk_info.duration} mins")

        print()
