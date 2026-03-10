"""
╔══════════════════════════════════════════════════════════════════╗
║     AI INTERVIEW - COMPUTER VISION MODULE  v3                   ║
╠══════════════════════════════════════════════════════════════════╣
║  FIXES IN v3:                                                    ║
║   ✓ Phone & objects now detected correctly (conf lowered + NMS) ║
║   ✓ Score changes live — drops on distraction, reflects reality ║
║   ✓ "person" class fully excluded from YOLO                     ║
║   ✓ Confirmation buffer fixed (was blocking ALL detections)     ║
║   ✓ Penalty is time-based (fair) not per-appearance only        ║
║   ✓ Distraction score is separate and visible in real time      ║
║   ✓ Debug mode: prints every YOLO detection to terminal         ║
╠══════════════════════════════════════════════════════════════════╣
║  INSTALL:                                                        ║
║   pip install opencv-python mediapipe deepface ultralytics numpy║
║  RUN:  python interview_cv_v3.py                                ║
║  KEYS: Q=quit  H=heatmap  P=pause  D=debug YOLO output          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import json
from datetime import datetime
from collections import defaultdict
from deepface import DeepFace
from ultralytics import YOLO

# ══════════════════════════════════════════════════════
#  CONFIG  — tune these to adjust sensitivity
# ══════════════════════════════════════════════════════
INTERVIEW_DURATION   = 0      # 0 = unlimited
EMOTION_EVERY_N_SEC  = 3
YOLO_EVERY_N_FRAMES  = 10     # run YOLO every 10 frames
YOLO_CONF            = 0.40   # lower = more sensitive (phone detection needs this)
YOLO_MODEL           = "yolov8s.pt"  # s is better than n for small objects like phones
GAZE_THRESHOLD       = 0.38
MULTI_FACE_LIMIT     = 1

# Confirmation: object must appear in this many consecutive YOLO
# runs to be "confirmed" — prevents single-frame ghosts
# Set to 1 to disable (detect immediately), 2-3 for stability
CONFIRM_RUNS_NEEDED  = 2

# Penalty drip: every YOLO run a confirmed object is present,
# this fraction of its penalty is subtracted from the score.
PENALTY_DRIP_RATE    = 0.15

# ── Face score fine-tuning ────────────────────────────────────────
# Presence: pts lost per frame the face is ABSENT (~0.08 = -2.4 pts/sec at 30fps)
PRESENCE_ABSENT_DRIP = 0.08

# Gaze: separate horizontal / vertical thresholds and penalties
# Horizontal (left/right) is penalized MORE — looking sideways = cheating risk
GAZE_H_THRESHOLD     = 0.28   # tighter threshold for left/right
GAZE_V_THRESHOLD     = 0.42   # looser threshold for up/down (normal in interviews)
GAZE_H_PENALTY_DRIP  = 0.06   # pts lost per frame looking left or right
GAZE_V_PENALTY_DRIP  = 0.02   # pts lost per frame looking up or down

# Emotion smoothing: rolling window to avoid single-frame jumps
EMOTION_SMOOTH_N     = 5

# Classes to ALWAYS ignore regardless of confidence
IGNORED_CLASSES = {
    "person", "chair", "couch", "bed", "dining table",
    "toilet", "sink", "refrigerator", "microwave", "oven",
    "toaster", "hair drier", "toothbrush", "wall", "ceiling",
}

# ── Distraction DB ────────────────────────────────────────────────
DISTRACTION_DB = {
    # CRITICAL
    "cell phone"   : {"severity": "CRITICAL", "penalty": 15, "emoji": "📱"},
    "laptop"       : {"severity": "CRITICAL", "penalty": 15, "emoji": "💻"},
    "tablet"       : {"severity": "CRITICAL", "penalty": 14, "emoji": "📟"},
    "tv"           : {"severity": "CRITICAL", "penalty": 12, "emoji": "📺"},
    "remote"       : {"severity": "CRITICAL", "penalty": 10, "emoji": "📡"},
    "keyboard"     : {"severity": "CRITICAL", "penalty": 8,  "emoji": "⌨️"},
    "mouse"        : {"severity": "CRITICAL", "penalty": 8,  "emoji": "🖱️"},
    # HIGH
    "book"         : {"severity": "HIGH",     "penalty": 10, "emoji": "📚"},
    "notebook"     : {"severity": "HIGH",     "penalty": 10, "emoji": "📓"},
    "magazine"     : {"severity": "HIGH",     "penalty": 8,  "emoji": "📰"},
    # MEDIUM
    "clock"        : {"severity": "MEDIUM",   "penalty": 3,  "emoji": "🕐"},
    # LOW
    "cup"          : {"severity": "LOW",      "penalty": 1,  "emoji": "☕"},
    "bottle"       : {"severity": "LOW",      "penalty": 1,  "emoji": "🍶"},
    "wine glass"   : {"severity": "LOW",      "penalty": 2,  "emoji": "🍷"},
    "bowl"         : {"severity": "LOW",      "penalty": 1,  "emoji": "🥣"},
    "cat"          : {"severity": "LOW",      "penalty": 2,  "emoji": "🐱"},
    "dog"          : {"severity": "LOW",      "penalty": 2,  "emoji": "🐶"},
    "backpack"     : {"severity": "LOW",      "penalty": 2,  "emoji": "🎒"},
    "scissors"     : {"severity": "LOW",      "penalty": 2,  "emoji": "✂️"},
}

SEVERITY_COLORS = {
    "CRITICAL": (0,   0,   255),
    "HIGH"    : (0,   100, 255),
    "MEDIUM"  : (0,   200, 255),
    "LOW"     : (0,   210, 120),
}

EMOTION_COLORS = {
    "happy"   : (0, 220, 0),
    "neutral" : (200, 200, 200),
    "surprise": (0, 165, 255),
    "fear"    : (80, 80, 255),
    "angry"   : (0, 0, 220),
    "sad"     : (150, 150, 255),
    "disgust" : (0, 100, 180),
}

# MediaPipe indices
LEFT_IRIS   = [474, 475, 476, 477]
RIGHT_IRIS  = [469, 470, 471, 472]
LEFT_EYE    = [362,382,381,380,374,373,390,249,263,466,388,387,386,385,384,398]
RIGHT_EYE   = [33,7,163,144,145,153,154,155,133,173,157,158,159,160,161,246]
NOSE_TIP    = 1
CHIN        = 152
LEFT_EYE_L  = 33
RIGHT_EYE_R = 263


# ══════════════════════════════════════════════════════
#  OBJECT TRACKER
# ══════════════════════════════════════════════════════
class ObjectTracker:
    def __init__(self):
        self.active      = {}
        self.durations   = defaultdict(float)
        self.appearances = defaultdict(int)
        self.timeline    = []

    def update(self, confirmed_names, now):
        s = set(confirmed_names)
        for n in s:
            if n not in self.active:
                self.active[n] = now
                self.appearances[n] += 1
                self.timeline.append((now, "APPEARED", n))
        for n in list(self.active):
            if n not in s:
                self.durations[n] += now - self.active[n]
                self.timeline.append((now, "LEFT", n))
                del self.active[n]

    def finalize(self, now):
        for n, t in self.active.items():
            self.durations[n] += now - t
        self.active = {}


# ══════════════════════════════════════════════════════
#  MAIN ANALYZER
# ══════════════════════════════════════════════════════
class InterviewAnalyzer:

    def __init__(self, debug=False):
        self.debug = debug
        print("\n[INFO] Loading models...")

        # MediaPipe
        mp_fm = mp.solutions.face_mesh
        mp_fd = mp.solutions.face_detection
        self.mp_draw        = mp.solutions.drawing_utils
        self.mp_draw_styles = mp.solutions.drawing_styles
        self.mp_fm_ref      = mp_fm

        self.face_mesh   = mp_fm.FaceMesh(
            max_num_faces=4, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.face_detect = mp_fd.FaceDetection(
            model_selection=1, min_detection_confidence=0.5)

        # YOLO
        print(f"[INFO] Loading {YOLO_MODEL} ...")
        self.yolo = YOLO(YOLO_MODEL)
        print("[INFO] ✓ Models loaded\n")

        # Stats
        self.stats = {
            "frames_total"        : 0,
            "frames_face_present" : 0,
            "frames_multi_face"   : 0,
            "frames_no_face"      : 0,
            "frames_eye_contact"  : 0,
            "frames_looking_away" : 0,
            "head_pose_counts"    : {"Forward":0,"Left":0,"Right":0,"Up":0,"Down":0},
            "emotions"            : [],
        }
        # Penalty accumulators for face metrics (0–100 each)
        self._presence_penalty   = 0.0   # grows when face absent
        self._gaze_penalty       = 0.0   # grows on horizontal/vertical deviation
        # Emotion smoothing buffer
        self._emotion_history    = []    # last N raw emotion strings

        # Distraction state
        self.obj_tracker     = ObjectTracker()
        self.heatmap         = None

        # Confirmation buffer: name → consecutive YOLO runs seen
        self._run_counter    = defaultdict(int)
        # Confirmed objects currently active
        self._confirmed_now  = set()
        # Accumulated penalty (0–100)
        self._dist_penalty   = 0.0

        # Timing
        self.session_start    = time.time()
        self.last_emotion_t   = 0
        self.frame_count      = 0
        self.paused           = False

        print("  Q = quit   H = heatmap   P = pause   D = toggle debug\n")

    # ──────────────────────────────────────────
    #  GAZE  (split H/V thresholds + direction label)
    # ──────────────────────────────────────────
    def get_gaze(self, lm, W, H):
        """
        Returns:
          gx          – horizontal iris displacement ratio (-0.5 … +0.5)
          gy          – vertical iris displacement ratio
          eye_contact – True only if both axes within their thresholds
          h_deviated  – True if horizontal deviation exceeds GAZE_H_THRESHOLD
          v_deviated  – True if vertical deviation exceeds GAZE_V_THRESHOLD
          direction   – "Center" | "Left" | "Right" | "Up" | "Down"
        """
        def ic(idx):
            return np.array([[lm[i].x*W, lm[i].y*H] for i in idx]).mean(0)
        def corners(idx):
            pts = np.array([[lm[i].x*W, lm[i].y*H] for i in idx])
            return pts[pts[:,0].argmin()], pts[pts[:,0].argmax()]
        try:
            li = ic(LEFT_IRIS);  ri = ic(RIGHT_IRIS)
            ll,lr = corners(LEFT_EYE); rl,rr = corners(RIGHT_EYE)
            gx = ((li[0]-ll[0])/(lr[0]-ll[0]+1e-6)-0.5 +
                  (ri[0]-rl[0])/(rr[0]-rl[0]+1e-6)-0.5) / 2
            lvy = (li[1]-lm[386].y*H)/(lm[374].y*H-lm[386].y*H+1e-6)-0.5
            rvy = (ri[1]-lm[159].y*H)/(lm[145].y*H-lm[159].y*H+1e-6)-0.5
            gy  = (lvy+rvy)/2

            h_dev = abs(gx) > GAZE_H_THRESHOLD
            v_dev = abs(gy) > GAZE_V_THRESHOLD
            contact = not h_dev and not v_dev

            if   h_dev and gx > 0: direction = "Right"
            elif h_dev and gx < 0: direction = "Left"
            elif v_dev and gy > 0: direction = "Down"
            elif v_dev and gy < 0: direction = "Up"
            else:                  direction = "Center"

            return gx, gy, contact, h_dev, v_dev, direction
        except Exception:
            return 0.0, 0.0, True, False, False, "Center"

    # ──────────────────────────────────────────
    #  HEAD POSE
    # ──────────────────────────────────────────
    def get_head_pose(self, lm, W, H):
        try:
            nose    = np.array([lm[NOSE_TIP].x*W,    lm[NOSE_TIP].y*H])
            le      = np.array([lm[LEFT_EYE_L].x*W,  lm[LEFT_EYE_L].y*H])
            re      = np.array([lm[RIGHT_EYE_R].x*W, lm[RIGHT_EYE_R].y*H])
            chin    = np.array([lm[CHIN].x*W,         lm[CHIN].y*H])
            mid     = (le+re)/2
            hx = (nose[0]-mid[0]) / (abs(re[0]-le[0])+1e-6)
            vy = (nose[1]-mid[1]) / (abs(chin[1]-mid[1])+1e-6)
            if   hx >  0.15: return "Left"
            elif hx < -0.15: return "Right"
            elif vy <  0.35: return "Up"
            elif vy >  0.60: return "Down"
            else:            return "Forward"
        except Exception:
            return "Forward"

    # ──────────────────────────────────────────
    #  EMOTION  (face-cropped + smoothed)
    # ──────────────────────────────────────────
    def get_emotion(self, frame, face_bbox=None):
        """
        Crops the face region before running DeepFace for better accuracy.
        face_bbox: (x1,y1,x2,y2) from MediaPipe or None (use full frame).
        Applies rolling smoothing over last EMOTION_SMOOTH_N readings.
        """
        try:
            H, W = frame.shape[:2]
            if face_bbox:
                x1,y1,x2,y2 = face_bbox
                pad = 20
                x1 = max(0, x1-pad); y1 = max(0, y1-pad)
                x2 = min(W, x2+pad); y2 = min(H, y2+pad)
                crop = frame[y1:y2, x1:x2]
                # Upscale small crops so DeepFace gets enough pixels
                if crop.shape[0] < 80 or crop.shape[1] < 80:
                    crop = cv2.resize(crop, (160,160))
            else:
                crop = frame

            r = DeepFace.analyze(crop, actions=["emotion"],
                                 enforce_detection=False, silent=True)
            r = r[0] if isinstance(r, list) else r
            raw = r.get("dominant_emotion", "neutral")
        except Exception:
            raw = "neutral"

        # Rolling smoothing: keep last N, return most frequent
        self._emotion_history.append(raw)
        if len(self._emotion_history) > EMOTION_SMOOTH_N:
            self._emotion_history.pop(0)

        # Most common emotion in window
        counts = {}
        for e in self._emotion_history:
            counts[e] = counts.get(e, 0) + 1
        return max(counts, key=counts.get)

    # ──────────────────────────────────────────
    #  YOLO — THE FIXED VERSION
    # ──────────────────────────────────────────
    def run_yolo(self, frame):
        """
        Returns list of CONFIRMED distraction object names.
        Logic:
          1. Run YOLO at YOLO_CONF threshold
          2. Skip ignored classes (person, furniture, etc.)
          3. Increment per-object run counter
          4. Object is 'confirmed' only after CONFIRM_RUNS_NEEDED consecutive runs
          5. Reset counter for objects not seen this run
        """
        seen_this_run = set()

        try:
            results = self.yolo(frame, conf=YOLO_CONF, verbose=False)[0]

            for box in results.boxes:
                raw_name = results.names[int(box.cls[0])]
                name     = raw_name.lower()
                conf     = float(box.conf[0])

                # Always skip ignored classes
                if name in IGNORED_CLASSES:
                    continue

                # Only care about objects in our distraction list
                if name not in DISTRACTION_DB:
                    if self.debug:
                        print(f"[YOLO] Ignored (not in DB): {name} {conf:.2f}")
                    continue

                seen_this_run.add(name)

                if self.debug:
                    print(f"[YOLO] Detected: {name} conf={conf:.2f} "
                          f"run_count={self._run_counter[name]+1}/{CONFIRM_RUNS_NEEDED}")

                # Draw bounding box even before confirmation (yellow = unconfirmed)
                x1,y1,x2,y2 = map(int, box.xyxy[0])
                info  = DISTRACTION_DB[name]
                sev   = info["severity"]

                if self._run_counter[name] + 1 >= CONFIRM_RUNS_NEEDED:
                    # CONFIRMED — use severity color
                    color = SEVERITY_COLORS[sev]
                    thick = 3 if sev == "CRITICAL" else 2
                else:
                    # UNCONFIRMED — yellow dashed-style
                    color = (0, 220, 220)
                    thick = 1

                cv2.rectangle(frame, (x1,y1), (x2,y2), color, thick)
                label = f"{info['emoji']} {name.upper()} {conf:.0%}"
                (tw,th),_ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.50, 2)
                cv2.rectangle(frame, (x1,y1-th-10), (x1+tw+8,y1), color, -1)
                cv2.putText(frame, label, (x1+4,y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255,255,255), 2, cv2.LINE_AA)
                # Severity badge
                cv2.rectangle(frame, (x2-70,y1), (x2,y1+18), color, -1)
                cv2.putText(frame, sev, (x2-68,y1+13),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255,255,255), 1, cv2.LINE_AA)

                # Update heatmap
                if self.heatmap is not None:
                    H,W = frame.shape[:2]
                    self.heatmap[max(0,y1):min(H,y2), max(0,x1):min(W,x2)] += 1.0

        except Exception as e:
            if self.debug:
                print(f"[YOLO] Error: {e}")

        # ── Update confirmation counters ──────────────────────────────
        # Increment for seen objects
        for name in seen_this_run:
            self._run_counter[name] += 1

        # Reset for objects NOT seen this run
        for name in list(self._run_counter.keys()):
            if name not in seen_this_run:
                if self.debug and self._run_counter[name] > 0:
                    print(f"[YOLO] Lost: {name}, resetting counter")
                self._run_counter[name] = 0
                self._confirmed_now.discard(name)

        # ── Build confirmed set ───────────────────────────────────────
        confirmed = []
        for name, count in self._run_counter.items():
            if count >= CONFIRM_RUNS_NEEDED:
                confirmed.append(name)
                self._confirmed_now.add(name)

        return confirmed

    # ──────────────────────────────────────────
    #  SCORES
    # ──────────────────────────────────────────
    def presence_score(self):
        """Starts at 30, drips down when face is absent."""
        return max(0.0, 30.0 - min(30.0, self._presence_penalty))

    def gaze_score(self):
        """Starts at 35, drips down on horizontal deviation (more) and vertical (less)."""
        return max(0.0, 35.0 - min(35.0, self._gaze_penalty))

    def head_score(self):
        P = max(1, self.stats["frames_face_present"])
        F = self.stats["head_pose_counts"]["Forward"]
        return (F/P) * 20.0

    def multi_face_penalty(self):
        T = max(1, self.stats["frames_total"])
        M = self.stats["frames_multi_face"]
        return min(15.0, (M/T)*40.0)

    def face_score(self):
        return max(0.0,
            self.presence_score() +
            self.gaze_score() +
            self.head_score() -
            self.multi_face_penalty()
        )

    def dist_score(self):
        # Score starts at 100, drops as penalty accumulates
        return max(0.0, 100.0 - min(100.0, self._dist_penalty))

    def unified_score(self):
        return round(self.face_score()*0.65 + self.dist_score()*0.35, 1)

    # ──────────────────────────────────────────
    #  HUD HELPERS
    # ──────────────────────────────────────────
    def _bar(self, frame, x, y, w, h, ratio, color):
        cv2.rectangle(frame, (x,y), (x+w,y+h), (40,40,55), -1)
        cv2.rectangle(frame, (x,y), (x+int(w*max(0,min(1,ratio))),y+h), color, -1)

    def _panel(self, frame, x, y, w, h, alpha=0.65):
        ov = frame.copy()
        cv2.rectangle(ov, (x,y), (x+w,y+h), (12,12,25), -1)
        cv2.addWeighted(ov, alpha, frame, 1-alpha, 0, frame)

    def _text(self, frame, text, x, y, color=(220,220,220), scale=0.52, bold=False):
        cv2.putText(frame, text, (x,y), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, color, 2 if bold else 1, cv2.LINE_AA)

    # ──────────────────────────────────────────
    #  LEFT PANEL — face metrics
    # ──────────────────────────────────────────
    def draw_left_panel(self, frame, fd):
        H,W = frame.shape[:2]
        pw  = 245
        self._panel(frame, 0, 0, pw, H)

        def p(txt, y, col=(210,210,210), sc=0.52, bold=False):
            self._text(frame, txt, 8, y, col, sc, bold)

        elapsed = int(time.time()-self.session_start)
        p("FACE  ANALYSIS", 24, (0,220,180), 0.58, True)
        cv2.line(frame,(0,32),(pw,32),(60,60,80),1)
        p(f"Time   {elapsed//60:02d}:{elapsed%60:02d}", 55)

        # Presence
        ps  = self.presence_score()
        col = (0,220,0) if ps>22 else (0,165,255) if ps>12 else (0,0,255)
        p(f"Presence   {ps:.0f}/30", 82, col)
        self._bar(frame, 8, 88, pw-16, 7, ps/30, col)

        # Eye contact / gaze
        gs  = self.gaze_score()
        col = (0,220,0) if gs>26 else (0,165,255) if gs>14 else (0,0,255)
        gdir= fd.get("gaze_dir","Center")
        p(f"Gaze {gdir:<7}  {gs:.0f}/35", 115, col)
        self._bar(frame, 8, 121, pw-16, 7, gs/35, col)

        # Faces
        fc  = fd["face_count"]
        col = (0,0,255) if fd["multi_face"] else (0,220,0)
        p(f"Faces      {fc}", 148, col)

        # Head pose
        col = (0,220,0) if fd["head_pose"]=="Forward" else (0,165,255)
        p(f"Head       {fd['head_pose']}", 170, col)

        # Gaze bar
        cv2.line(frame,(0,182),(pw,182),(60,60,80),1)
        p("GAZE TRACKER", 198, (0,200,255), 0.48)
        bx,by,bw2 = 8,205,pw-16
        cv2.rectangle(frame,(bx,by),(bx+bw2,by+10),(40,40,55),-1)
        gp = int(bx + bw2/2 + fd["gaze_x"]*bw2*1.4)
        gp = max(bx, min(bx+bw2, gp))
        # Color: red if horizontal deviation, orange if vertical, green if center
        if fd.get("h_dev"):   gc = (0,0,255)
        elif fd.get("v_dev"): gc = (0,165,255)
        else:                  gc = (0,220,0)
        cv2.circle(frame,(gp,by+5),8,gc,-1)
        # Zone markers
        zone_l = int(bx + bw2/2 - GAZE_H_THRESHOLD*bw2*1.4)
        zone_r = int(bx + bw2/2 + GAZE_H_THRESHOLD*bw2*1.4)
        cv2.line(frame,(zone_l,by),(zone_l,by+10),(100,100,100),1)
        cv2.line(frame,(zone_r,by),(zone_r,by+10),(100,100,100),1)
        p("L",218,sc=0.38)
        cv2.putText(frame,"R",(pw-14,218),cv2.FONT_HERSHEY_SIMPLEX,0.38,(180,180,180),1)

        # Emotion
        cv2.line(frame,(0,228),(pw,228),(60,60,80),1)
        p("EMOTION", 244, (0,200,255), 0.48)
        ec = EMOTION_COLORS.get(fd["emotion"],(200,200,200))
        p(f"  {fd['emotion'].capitalize()}", 265, ec, 0.60, True)

        # Face score breakdown
        cv2.line(frame,(0,278),(pw,278),(60,60,80),1)
        fs  = self.face_score()
        fsc = (0,220,0) if fs>75 else (0,165,255) if fs>50 else (0,0,255)
        p("FACE SCORE", 296, (0,200,255), 0.48)
        p(f"  {fs:.0f} / 85", fsc, 0.72, True) if False else \
        p(f"  {fs:.0f} / 85", 320, fsc, 0.72, True)
        hs = self.head_score()
        p(f"  head:{hs:.0f}  multi:-{self.multi_face_penalty():.0f}", 342, (150,150,150), 0.42)

        return frame

    # ──────────────────────────────────────────
    #  RIGHT PANEL — distraction monitor
    # ──────────────────────────────────────────
    def draw_right_panel(self, frame, confirmed_now):
        H,W  = frame.shape[:2]
        pw   = 255
        sx   = W-pw
        self._panel(frame, sx, 0, pw, H)

        def p(txt, y, col=(210,210,210), sc=0.52, bold=False):
            self._text(frame, txt, sx+8, y, col, sc, bold)

        p("DISTRACTION MONITOR", 24, (0,220,180), 0.55, True)
        cv2.line(frame,(sx,32),(W,32),(60,60,80),1)

        # Active now
        p("ACTIVE NOW", 52, (0,200,255), 0.48)
        if confirmed_now:
            y = 72
            for name in list(confirmed_now)[:6]:
                info = DISTRACTION_DB.get(name,{})
                col  = SEVERITY_COLORS.get(info.get("severity","LOW"),(200,200,200))
                p(f"{info.get('emoji','•')} {name[:24]}", y, col, 0.50)
                y += 20
        else:
            p("  ✓  Clear", 72, (0,220,100))

        cv2.line(frame,(sx,175),(W,175),(60,60,80),1)

        # Total seen
        p("TOTAL SEEN", 192, (0,200,255), 0.48)
        y = 210
        for name,cnt in sorted(self.obj_tracker.appearances.items(),
                                key=lambda x:-x[1])[:5]:
            dur  = self.obj_tracker.durations.get(name,0)
            info = DISTRACTION_DB.get(name,{})
            col  = SEVERITY_COLORS.get(info.get("severity","LOW"),(200,200,200))
            p(f"{name[:16]}  x{cnt}  {dur:.0f}s", y, col, 0.46)
            y += 20

        cv2.line(frame,(sx,320),(W,320),(60,60,80),1)

        # Distraction score — THIS NOW CHANGES LIVE
        ds  = self.dist_score()
        dsc = (0,220,0) if ds>80 else (0,165,255) if ds>50 else (0,0,255)
        p("DISTRACT SCORE", 340, (0,200,255), 0.48)
        p(f"  {ds:.1f} / 100", 365, dsc, 0.72, True)
        # Show how much penalty so far
        p(f"  penalty: -{self._dist_penalty:.1f} pts", 385, (150,150,150), 0.44)
        self._bar(frame, sx+8, 392, pw-16, 8, ds/100, dsc)

        # Severity legend
        cv2.line(frame,(sx,408),(W,408),(60,60,80),1)
        p("SEVERITY KEY", 424, (160,160,160), 0.44)
        for i,(sev,col) in enumerate(SEVERITY_COLORS.items()):
            p(f"■ {sev}", 442+i*17, col, 0.42)

        return frame

    # ──────────────────────────────────────────
    #  BOTTOM BAR — unified score
    # ──────────────────────────────────────────
    def draw_bottom_bar(self, frame, paused):
        H,W   = frame.shape[:2]
        bh    = 46
        lp,rp = 245, 255
        self._panel(frame, lp, H-bh, W-rp-lp, bh, 0.75)

        us  = self.unified_score()
        col = (0,220,0) if us>75 else (0,165,255) if us>50 else (0,0,255)

        bx = lp+10; bw2 = W-rp-lp-20
        self._bar(frame, bx, H-bh+6, bw2, 10, us/100, col)

        label = f"UNIFIED SCORE:  {us} / 100"
        if paused: label += "   [ PAUSED ]"
        (tw,_),_ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
        cv2.putText(frame, label,
                    (lp+(W-rp-lp)//2-tw//2, H-8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, col, 2, cv2.LINE_AA)
        return frame

    # ──────────────────────────────────────────
    #  ALERT FLASH
    # ──────────────────────────────────────────
    def draw_alerts(self, frame, confirmed_now, multi_face):
        H,W   = frame.shape[:2]
        lp,rp = 245, 255
        blink = int(time.time()*3)%2==0

        critical = [n for n in confirmed_now
                    if DISTRACTION_DB.get(n,{}).get("severity")=="CRITICAL"]
        if critical and blink:
            cv2.rectangle(frame,(lp,0),(W-rp,42),(0,0,180),-1)
            cv2.putText(frame,
                        f"  CRITICAL OBJECT: {', '.join(critical).upper()}",
                        (lp+8,28), cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,(255,255,255),2,cv2.LINE_AA)

        if multi_face and blink:
            y0 = 46 if critical else 0
            cv2.rectangle(frame,(lp,y0),(W-rp,y0+42),(120,0,0),-1)
            cv2.putText(frame,"  ⚠ MULTIPLE FACES — CHEATING RISK",
                        (lp+8,y0+28),cv2.FONT_HERSHEY_SIMPLEX,
                        0.62,(255,255,255),2,cv2.LINE_AA)
        return frame

    # ──────────────────────────────────────────
    #  HEATMAP
    # ──────────────────────────────────────────
    def apply_heatmap(self, frame):
        if self.heatmap is None:
            return frame
        n = cv2.normalize(self.heatmap,None,0,255,cv2.NORM_MINMAX).astype(np.uint8)
        return cv2.addWeighted(frame, 0.60,
                               cv2.applyColorMap(n,cv2.COLORMAP_JET), 0.40, 0)

    # ──────────────────────────────────────────
    #  REPORT
    # ──────────────────────────────────────────
    def generate_report(self, name):
        now = time.time()
        self.obj_tracker.finalize(now)
        T   = max(1,self.stats["frames_total"])
        P   = max(1,self.stats["frames_face_present"])
        emo = {}
        for e in self.stats["emotions"]:
            emo[e] = emo.get(e,0)+1
        dom_emo = max(emo,key=emo.get) if emo else "neutral"

        objs = {}
        for n in self.obj_tracker.appearances:
            info = DISTRACTION_DB.get(n,{})
            objs[n] = {
                "severity"       : info.get("severity","LOW"),
                "appearances"    : self.obj_tracker.appearances[n],
                "visible_seconds": round(self.obj_tracker.durations[n],1),
                "penalty"        : info.get("penalty",2),
                "emoji"          : info.get("emoji","•"),
            }

        return {
            "candidate"        : name,
            "timestamp"        : datetime.now().isoformat(),
            "duration_seconds" : int(now-self.session_start),
            "scores": {
                "unified"      : self.unified_score(),
                "face"         : round(self.face_score(),1),
                "distraction"  : round(self.dist_score(),1),
            },
            "face_metrics": {
                "presence_pct"      : round(self.stats["frames_face_present"]/T*100,1),
                "eye_contact_pct"   : round(self.stats["frames_eye_contact"]/P*100,1),
                "multi_face_pct"    : round(self.stats["frames_multi_face"]/T*100,1),
                "head_pose"         : self.stats["head_pose_counts"],
                "dominant_emotion"  : dom_emo,
                "emotion_dist"      : emo,
            },
            "distraction_metrics": {
                "total_penalty"  : round(self._dist_penalty,2),
                "objects"        : objs,
                "critical_found" : [n for n,v in objs.items() if v["severity"]=="CRITICAL"],
            },
            "timeline": [
                {"t": round(t-self.session_start,1), "event": ev, "object": n}
                for t,ev,n in self.obj_tracker.timeline
            ],
            "flags": {
                "cheating_risk"          : self.stats["frames_multi_face"]>10,
                "low_presence"           : self.stats["frames_face_present"]/T < 0.7,
                "poor_eye_contact"       : self.stats["frames_eye_contact"]/P < 0.5,
                "electronic_device_found": any(n in ["cell phone","laptop","tablet","tv"]
                                               for n in objs),
                "reading_material_found" : any(n in ["book","notebook","magazine"]
                                               for n in objs),
            }
        }

    def save_report(self, report, path="report"):
        with open(f"{path}.json","w") as f:
            json.dump(report, f, indent=2)

        with open(f"{path}.txt","w") as f:
            ln = "═"*56
            f.write(f"{ln}\n   AI INTERVIEW — FULL CV REPORT\n{ln}\n\n")
            f.write(f"  Candidate : {report['candidate']}\n")
            f.write(f"  Time      : {report['timestamp']}\n")
            f.write(f"  Duration  : {report['duration_seconds']}s\n\n")
            s = report["scores"]
            f.write(f"  ★ UNIFIED SCORE  : {s['unified']} / 100\n")
            f.write(f"  ✦ Face Score     : {s['face']} / 100\n")
            f.write(f"  ✦ Distract Score : {s['distraction']} / 100\n\n")
            m = report["face_metrics"]
            f.write(f"── FACE ───────────────────────────────────────────\n")
            f.write(f"  Presence       : {m['presence_pct']}%\n")
            f.write(f"  Eye Contact    : {m['eye_contact_pct']}%\n")
            f.write(f"  Multi-Face     : {m['multi_face_pct']}%\n")
            f.write(f"  Dominant Emo   : {m['dominant_emotion']}\n")
            f.write(f"  Head Pose      : {m['head_pose']}\n\n")
            f.write(f"── DISTRACTIONS ───────────────────────────────────\n")
            d = report["distraction_metrics"]
            f.write(f"  Total Penalty  : -{d['total_penalty']} pts\n")
            if d["objects"]:
                for n,v in sorted(d["objects"].items(),key=lambda x:-x[1]["penalty"]):
                    f.write(f"  {v['emoji']} {n:<20} [{v['severity']:<8}] "
                            f"x{v['appearances']}  {v['visible_seconds']}s\n")
            else:
                f.write("  ✓ None detected\n")
            f.write(f"\n── FLAGS ───────────────────────────────────────────\n")
            for k,v in report["flags"].items():
                f.write(f"  {'⚠ YES' if v else '✓ NO '} — {k}\n")
            f.write(f"\n{ln}\n")

        print(f"[INFO] Saved → {path}.json & {path}.txt")

    def print_summary(self, r):
        s = r["scores"]
        print("\n"+"═"*48)
        print("   FINAL SUMMARY")
        print("═"*48)
        print(f"  ★ Unified Score   : {s['unified']} / 100")
        print(f"  ✦ Face Score      : {s['face']} / 100")
        print(f"  ✦ Distract Score  : {s['distraction']} / 100")
        for k,v in r["flags"].items():
            print(f"  {'⚠' if v else '✓'} {k}")
        print("═"*48)

    # ──────────────────────────────────────────
    #  MAIN LOOP
    # ──────────────────────────────────────────
    def run(self, candidate_name="Candidate"):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] Cannot open webcam"); return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        cur_emotion      = "neutral"
        cur_gaze_x       = 0.0
        cur_gaze_y       = 0.0
        cur_eye_contact  = True
        cur_h_dev        = False
        cur_v_dev        = False
        cur_gaze_dir     = "Center"
        cur_head_pose    = "Forward"
        cur_confirmed    = set()
        face_count       = 0
        multi_face       = False
        show_heatmap     = False

        mp_fm = mp.solutions.face_mesh
        print(f"[INFO] Session started: {candidate_name}\n")

        # Init heatmap once we know frame size
        ret, test_frame = cap.read()
        if ret:
            self.heatmap = np.zeros(test_frame.shape[:2], dtype=np.float32)

        while True:
            ret, frame = cap.read()
            if not ret: break

            if self.paused:
                cv2.putText(frame,"PAUSED — press P to resume",
                            (50,60),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,200,255),2)
                cv2.imshow("AI Interview", frame)
                key = cv2.waitKey(30)&0xFF
                if key==ord('p'): self.paused=False
                if key==ord('q'): break
                continue

            frame = cv2.flip(frame,1)
            H,W   = frame.shape[:2]
            self.frame_count += 1
            self.stats["frames_total"] += 1
            now = time.time()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # ── Face detection ──────────────────────────────
            det = self.face_detect.process(rgb)
            face_count  = len(det.detections) if det.detections else 0
            face_present= face_count >= 1
            multi_face  = face_count > MULTI_FACE_LIMIT

            if face_present:
                self.stats["frames_face_present"] += 1
            else:
                self.stats["frames_no_face"] += 1
                # Presence drips FASTER when face absent
                self._presence_penalty = min(30.0,
                    self._presence_penalty + PRESENCE_ABSENT_DRIP)
            if multi_face: self.stats["frames_multi_face"] += 1

            # ── Face mesh ───────────────────────────────────
            face_bbox = None
            cur_h_dev = False; cur_v_dev = False; cur_gaze_dir = "Center"
            mesh = self.face_mesh.process(rgb)
            if mesh.multi_face_landmarks:
                lm = mesh.multi_face_landmarks[0].landmark
                cur_gaze_x, cur_gaze_y, cur_eye_contact, cur_h_dev, cur_v_dev, cur_gaze_dir = \
                    self.get_gaze(lm, W, H)
                cur_head_pose = self.get_head_pose(lm, W, H)

                if cur_eye_contact:
                    self.stats["frames_eye_contact"] += 1
                else:
                    self.stats["frames_looking_away"] += 1
                    # Apply gaze penalty — horizontal costs more
                    if cur_h_dev:
                        self._gaze_penalty = min(35.0,
                            self._gaze_penalty + GAZE_H_PENALTY_DRIP)
                    if cur_v_dev:
                        self._gaze_penalty = min(35.0,
                            self._gaze_penalty + GAZE_V_PENALTY_DRIP)

                self.stats["head_pose_counts"][cur_head_pose] += 1

                # Build face bounding box for emotion crop
                xs = [lm[i].x*W for i in range(0,468)]
                ys = [lm[i].y*H for i in range(0,468)]
                face_bbox = (int(min(xs)),int(min(ys)),int(max(xs)),int(max(ys)))

                self.mp_draw.draw_landmarks(
                    frame,
                    mesh.multi_face_landmarks[0],
                    mp_fm.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_draw_styles
                        .get_default_face_mesh_iris_connections_style()
                )

            # ── Emotion (cropped + smoothed) ─────────────────
            if now-self.last_emotion_t >= EMOTION_EVERY_N_SEC and face_present:
                cur_emotion = self.get_emotion(frame, face_bbox)
                self.stats["emotions"].append(cur_emotion)
                self.last_emotion_t = now

            # ── YOLO ────────────────────────────────────────
            if self.frame_count % YOLO_EVERY_N_FRAMES == 0:
                cur_confirmed = set(self.run_yolo(frame))
                self.obj_tracker.update(cur_confirmed, now)

                # Apply time-based penalty drip for each active confirmed object
                for name in cur_confirmed:
                    info = DISTRACTION_DB.get(name, {})
                    drip = info.get("penalty", 2) * PENALTY_DRIP_RATE
                    self._dist_penalty = min(100.0, self._dist_penalty + drip)
                    if self.debug:
                        print(f"[SCORE] Penalty drip: +{drip:.2f} for {name} "
                              f"→ total={self._dist_penalty:.2f}  "
                              f"dist_score={self.dist_score():.1f}")

            # ── Heatmap ─────────────────────────────────────
            if show_heatmap:
                frame = self.apply_heatmap(frame)

            # ── Draw HUD ────────────────────────────────────
            fd = {
                "face_count" : face_count,
                "multi_face" : multi_face,
                "eye_contact": cur_eye_contact,
                "gaze_x"     : cur_gaze_x,
                "gaze_y"     : cur_gaze_y,
                "gaze_dir"   : cur_gaze_dir,
                "h_dev"      : cur_h_dev,
                "v_dev"      : cur_v_dev,
                "head_pose"  : cur_head_pose,
                "emotion"    : cur_emotion,
            }
            frame = self.draw_left_panel(frame, fd)
            frame = self.draw_right_panel(frame, cur_confirmed)
            frame = self.draw_bottom_bar(frame, self.paused)
            frame = self.draw_alerts(frame, cur_confirmed, multi_face)

            # ── Time limit ──────────────────────────────────
            if INTERVIEW_DURATION>0 and (now-self.session_start)>=INTERVIEW_DURATION:
                print("[INFO] Time limit reached."); break

            cv2.imshow("AI Interview  (Q=quit | H=heatmap | P=pause | D=debug)", frame)
            key = cv2.waitKey(1)&0xFF
            if   key==ord('q'): break
            elif key==ord('h'): show_heatmap = not show_heatmap
            elif key==ord('p'): self.paused = True
            elif key==ord('d'):
                self.debug = not self.debug
                print(f"[INFO] Debug mode: {'ON' if self.debug else 'OFF'}")

        cap.release()
        cv2.destroyAllWindows()

        report = self.generate_report(candidate_name)
        slug   = candidate_name.replace(" ","_")
        self.save_report(report, path=f"interview_report_{slug}")
        self.print_summary(report)
        return report


# ══════════════════════════════════════════════════════
#  ENTRY
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("╔═══════════════════════════════════════════════╗")
    print("║   AI INTERVIEW — CV ANALYSIS SYSTEM  v3      ║")
    print("╚═══════════════════════════════════════════════╝\n")
    name  = input("Candidate name     : ").strip() or "Candidate"
    dbg   = input("Enable debug mode? [y/N]: ").strip().lower() == "y"
    InterviewAnalyzer(debug=dbg).run(candidate_name=name)
