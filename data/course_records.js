// course_records.js
const courseRecordsMaster = [
  {
    "stage": 0,
    "route": "Llanthony to Grosmont",
    "distance_miles": 11.4,
    "overall_record": {
      "time": "01:08:30",
      "runner": "Martin Norton",
      "club": "Lliswerry Runners",
      "year": "2018"
    },
    "female_record": null,
    "notes": "Stage 0 route run 2018 only"
  },
  {
    "stage": 1,
    "route": "Grosmont to Skenfrith",
    "distance_miles": 5.1,
    "overall_record": {
      "time": "00:29:02",
      "runner": "Michael Lewis",
      "club": "Fairwater Cwmbran",
      "year": "2018"
    },
    "female_record": {
      "time": "00:29:16",
      "runner": "Emily Davies",
      "club": "Neath",
      "year": "2026"
    },
    "notes": ""
  },
  {
    "stage": 2,
    "route": "Skenfrith to Whitecastle",
    "distance_miles": 6.9,
    "overall_record": {
      "time": "00:40:57",
      "runner": "Unknown Runner",
      "club": "Unknown Club",
      "year": "???"
    },
    "female_record": {
      "time": "00:42:40",
      "runner": "Lauren Cooper",
      "club": "Parc Bryn Bach RC",
      "year": "2023"
    },
    "notes": "pre 2006 records"
  },
  {
    "stage": 3,
    "route": "Whitecastle to Abergavenny",
    "distance_miles": 7.5,
    "overall_record": {
      "time": "00:41:44",
      "runner": "Tom McCarthy",
      "club": "Pontypridd",
      "year": "2026"
    },
    "female_record": {
      "time": "00:47:30",
      "runner": "Emily Lagomarsino",
      "club": "San Domenico RC",
      "year": "2017"
    },
    "notes": ""
  },
  {
    "stage": 4,
    "route": "Abergavenny to Hen Gwrt Moat",
    "distance_miles": 6.7,
    "overall_record": {
      "time": "00:36:47",
      "runner": "Phillip Matthews",
      "club": "Parc Bryn Bach",
      "year": "2025"
    },
    "female_record": {
      "time": "00:42:06",
      "runner": "Antoinette Rose",
      "club": "Lliswerry Runners",
      "year": "2023"
    },
    "notes": "Shorter revised route introduced 2014"
  },
  {
    "stage": 5,
    "route": "Hen Gwrt Moat to Monmouth",
    "distance_miles": 8.1,
    "overall_record": {
      "time": "00:42:40",
      "runner": "Lloyd Cottrell",
      "club": "Parc Bryn Bach",
      "year": "2025"
    },
    "female_record": {
      "time": "00:50:40",
      "runner": "Kath Matthews",
      "club": "Chepstow Harriers",
      "year": "2022"
    },
    "notes": "Longer revised route introduced 2014"
  },
  {
    "stage": 6,
    "route": "Monmouth to Raglan",
    "distance_miles": 12.5,
    "overall_record": {
      "time": "01:06:45",
      "runner": "Daniel Bodman",
      "club": "Parc Bryn Bach",
      "year": "2025"
    },
    "female_record": {
      "time": "01:24:12",
      "runner": "Tracy Jenkins",
      "club": "Porthcawl",
      "year": "2026"
    },
    "notes": "Shorter revised route introduced 2022"
  },
  {
    "stage": 7,
    "route": "Raglan to Usk",
    "distance_miles": 5.5,
    "overall_record": {
      "time": "00:31:40",
      "runner": "Peter Coles",
      "club": "Pontypridd Roadents",
      "year": "2014"
    },
    "female_record": {
      "time": "00:34:31",
      "runner": "Nicola Jukes",
      "club": "Parc Bryn Bach RC",
      "year": "2023"
    },
    "notes": "Shorter revised route introduced 2022"
  },
  {
    "stage": 8,
    "route": "Usk to Tintern",
    "distance_miles": 13.1,
    "overall_record": {
      "time": "01:12:40",
      "runner": "Jake Tasker",
      "club": "Ogmore Phoenix",
      "year": "2024"
    },
    "female_record": {
      "time": "01:20:39",
      "runner": "Clara Evans",
      "club": "Pontypridd Roadents",
      "year": "2023"
    },
    "notes": ""
  },
  {
    "stage": 9,
    "route": "Tintern to Chepstow",
    "distance_miles": 10.0,
    "overall_record": {
      "time": "00:54:33",
      "runner": "Daniel Bodman",
      "club": "Aberdare Valley",
      "year": "2019"
    },
    "female_record": {
      "time": "01:04:54",
      "runner": "Kath Matthews",
      "club": "Chepstow Harriers",
      "year": "2017"
    },
    "notes": ""
  },
  {
    "stage": 10,
    "route": "Chepstow to Caldicot",
    "distance_miles": 6.6,
    "overall_record": {
      "time": "00:46:14",
      "runner": "Sam Lewis Jones",
      "club": "Parc Bryn Bach",
      "year": "2026"
    },
    "female_record": {
      "time": "00:50:33",
      "runner": "Lauren Cooper",
      "club": "Parc Bryn Bach RC",
      "year": "2025"
    },
    "notes": "Longer revised route introduced 2025"
  },
  {
    "stage": 11,
    "route": "Caldicot to Penhow",
    "distance_miles": 8.3,
    "overall_record": {
      "time": "00:46:46",
      "runner": "Josh Fitton",
      "club": "Lliswerry",
      "year": "2026"
    },
    "female_record": {
      "time": "00:54:01",
      "runner": "Kath Matthews",
      "club": "Chepstow Harriers",
      "year": "2018"
    },
    "notes": "Longer revised route introduced 2015"
  },
  {
    "stage": 12,
    "route": "Penhow to Caerleon",
    "distance_miles": 6.4,
    "overall_record": {
      "time": "00:34:50",
      "runner": "Lloyd Cottrell",
      "club": "Lliswerry",
      "year": "2024"
    },
    "female_record": {
      "time": "00:38:11",
      "runner": "Antoinette Rose",
      "club": "Lliswerry Runners",
      "year": "2026"
    },
    "notes": "Shorter revised route introduced 2024"
  },
  {
    "stage": 13,
    "route": "Caerleon to Castell Y Bwch",
    "distance_miles": 5.4,
    "overall_record": {
      "time": "00:31:55",
      "runner": "Daniel Bodman",
      "club": "Parc Bryn Bach",
      "year": "2024"
    },
    "female_record": {
      "time": "00:36:52",
      "runner": "Emma Wookey",
      "club": "Lliswerry Runners",
      "year": "2025"
    },
    "notes": ""
  },
  {
    "stage": 14,
    "route": "Castell Y Bwch to Olive Tree",
    "distance_miles": 5.1,
    "overall_record": {
      "time": "00:28:42",
      "runner": "Aiden Zembrzuski",
      "club": "Builth & District",
      "year": "2026"
    },
    "female_record": {
      "time": "00:35:03",
      "runner": "Maisie Pearce",
      "club": "Parc Bryn Bach",
      "year": "2026"
    },
    "notes": "New stage first run 2026"
  }
];