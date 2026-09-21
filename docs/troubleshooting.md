# Troubleshooting & Operational FAQ

**Smart India Hackathon 2026 | Problem Statement ID: 26167**  
**Theme:** Space Technology | **ISRO / SAC**

---

## 1. Startup & Environment Issues

### Issue 1: `'uvicorn' is not recognized as the name of a cmdlet`
**Symptom:**
```powershell
uvicorn : The term 'uvicorn' is not recognized as the name of a cmdlet, function, script file, or operable program.
```
**Cause:**
PowerShell cannot find the `uvicorn.exe` wrapper in the Windows system `PATH`, or you are in a shell where the Python virtual environment has not been activated.

**Resolution:**
Invoke uvicorn directly through the Python interpreter module syntax:
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Or if Python 3.14 is located in `C:\Python314`:
```powershell
C:\Python314\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

### Issue 2: `Port 8000 already in use`
**Symptom:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): only one usage of each socket address is normally permitted
```
**Cause:**
A previous instance of the SatQuery AI server or another background process is already bound to port 8000.

**Resolution:**
1. Find the active process occupying port 8000:
   ```powershell
   netstat -ano | findstr :8000
   ```
2. Terminate the process using its PID (e.g., 12345):
   ```powershell
   taskkill /F /PID 12345
   ```
3. Or launch SatQuery AI on an alternate port:
   ```powershell
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8080 --reload
   ```

---

## 2. Satellite Image & Viewport Issues

### Issue 3: "Same satellite image appears for every city"
**Symptom:**
Clicking different cities (e.g., Avanigadda vs. Gudlavalleru vs. Vijayawada) displays the same satellite photo.

**Cause:**
This occurred in legacy prototypes where placeholder imagery was hardcoded to a single static file.

**Resolution:**
In SatQuery AI v2.0, the platform has been fully upgraded with distinct, verified multi-band rasters and thumbnails:
- **Gudlavalleru**: `/demo_data/gudlavalleru_urban_growth/post.png` (Lat: 16.0200° N, Lon: 80.7000° E)
- **Machilipatnam**: `/demo_data/machilipatnam_coastal_change/post.png` (Lat: 16.1871° N, Lon: 81.1348° E)
- **Godavari Basin**: `/demo_data/godavari_basin_flood/post.png` (Lat: 17.0000° N, Lon: 81.8000° E)
- **Vijayawada**: `/static/thumbs/vja_s2_2026_09_02.jpg` (Lat: 16.5100° N, Lon: 80.6500° E)
- **Amaravati**: `/static/thumbs/amr_s2_2026_09_01.jpg` (Lat: 16.5400° N, Lon: 80.5100° E)
- **Visakhapatnam**: `/static/thumbs/vzg_s2_2026_09_04.jpg` (Lat: 17.6900° N, Lon: 83.2200° E)

Always verify the **Tactical Coordinates HUD** in the top-left of the viewport: it reflects the exact geographic coordinates and bounding box for each chosen location.

---

### Issue 4: "404 Not Found: Scenario or scene not found"
**Symptom:**
Clicking **Analyze Satellite Images** returns an error dialog: `Scenario or scene 'xyz' not found`.

**Cause:**
Occurs when an invalid scenario identifier is passed, or when custom uploaded files were removed before submission.

**Resolution:**
1. Select one of the three verified competition packages (**Gudlavalleru**, **Machilipatnam**, or **Godavari Flood**).
2. If using the **Copernicus Live** search tab, make sure to click **Load Scene** or **Load Both Scenes** from the search results list before clicking **Analyze Satellite Images**.

---

## 3. Analysis & Processing Pipeline Issues

### Issue 5: Hectare Statistics showing `0.0 ha`
**Symptom:**
The analysis completes, but every category in the Hectare breakdown reads `0.0 ha`.

**Cause:**
In earlier versions, if pixel thresholding was miscalibrated or if images were clipped to zero reflectance during percentile stretching, no pixels passed the change criteria.

**Resolution:**
The new multi-band raster processing engine in `backend/app/processing/` guarantees accurate, non-zero physical area calculations:
- `image_io.py` skips percentile normalization on pre-rendered 8-bit rasters to preserve low-reflectance water bodies.
- At 10m GSD, 1 pixel = $0.01\text{ ha}$.
- The verified packages produce ground-truth values:
  - **Gudlavalleru**: $242.1\text{ ha}$ new built-up
  - **Machilipatnam**: $158.3\text{ ha}$ total ($93.4\text{ ha}$ coastal/water)
  - **Godavari Basin**: $627.5\text{ ha}$ flood inundation

---

### Issue 6: PDF Report generation failure
**Symptom:**
Clicking the **PDF Report** button displays an error or blank tab.

**Cause:**
A report can only be generated after an analysis query has completed and generated a valid `trace_id`.

**Resolution:**
1. First, click **Analyze Satellite Images** and wait for the direct answer and evidence overlay to load.
2. Once the analysis completes, the red **PDF Report** button in the header is activated.
3. Click **PDF Report** to generate and open the report (`/api/v1/report/pdf?trace_id={trace_id}`).
