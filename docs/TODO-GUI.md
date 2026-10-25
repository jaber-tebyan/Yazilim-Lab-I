# GUI TODO — Campus Resource Reservation System (PySide6)

Reference: `Yaz_Lab_I.txt` Section 7 ("Masaüstü uygulaması").

---

## 1. Setup & Architecture
- [x] Base GUI entrypoint & window shell (`src/yazilim_lab_project/gui/app.py`, `src/yazilim_lab_project/gui/main_window.py`)
- [x] Connect GUI state strictly to `Engine` and `AppState` without duplicating business rules
- [x] PySide6 script launcher in `pyproject.toml` (`yazilim-lab-gui`)

## 2. Requirement 1: Initial Data Picker (Başlangıç Dosyası Seçimi)
- [x] File dialog to pick any `baslangic.json`
- [x] Clean re-initialization of `AppState` and `Engine` on file load
- [x] Automatic refresh of all panels, calendar, and lists upon state change

## 3. Requirement 2: Resource Calendar / Timeline Grid (Kaynak Takvimi)
- [x] Horizontal time axis from 08:00 to 22:00 with 15-minute grid markings
- [x] Dedicated row for each resource, date picker to switch displayed day
- [x] Colored reservation blocks by status (`ONAYLI`, `KULLANIMDA`, `TAMAMLANDI`, `IPTAL`, `GELMEDI`)
- [x] Distinct visual styling for maintenance windows (`BAKIM`) and prep times (`HAZIRLIK`)
- [x] Sub-row rendering for overlapping `IPTAL`/`GELMEDI` with newly placed reservations on the same resource
- [x] Simulated clock indicator line on the calendar
- [x] Click reservation block to view details (id, user, interval, price, status, package) and trigger actions

## 4. Requirement 3: Demand / Booking Form (Talep Formu)
- [x] Form for single reservation and multi-item package reservation (2–4 items)
- [x] Dynamic price preview button/trigger calling `fiyat` rule/interface
- [x] Immediate display of rejection error code & Turkish description, or confirmation details (id, price, balance)
- [x] Itemized status table for `PAKET_RED` showing which items passed and which failed

## 5. Requirement 4: User Panel (Kullanıcı Paneli)
- [x] User selector dropdown/list (no login screen required)
- [x] Real-time display of user's KP balance, weekly quota, and reliability score (0–100)
- [x] Tables/lists of selected user's active/past reservations and waiting list entries

## 6. Requirement 5: Reservation Actions & Auto-Waiting Prompt (Eylemler)
- [ ] Action buttons for check-in (`giris`), check-out (`cikis`), and cancellation (`iptal`) directly from the selected reservation
- [ ] Display refund, balance change, reliability delta, and triggered `OTOMATIK_ATAMA`
- [ ] When a reservation request returns `KESISME` or `HAZIRLIK_IHLALI`, prompt user to join waiting list (`bekleme`) without re-entering parameters

## 7. Requirement 6: Simulated Clock Controls (Simüle Saat Denetimi)
- [ ] Persistent clock display on screen
- [ ] Advance clock dialog/controls (`saat` command) with chronological event log viewer (`TAMAMLANDI`, `GELMEDI`, `OTOMATIK_ATAMA`, `HAFTALIK_SIFIRLAMA`)

## 8. Requirement 7: Session Audit Log (Olay Günlüğü)
- [ ] Chronological table of all commands and results executed during the session
- [ ] Selecting a row reveals formatted JSON command and JSON result

## 9. Requirements 8 & 9: Dynamic User & Resource Creation (Yeni Üye ve Kaynak Ekleme)
- [ ] Dialog to add user (`kullanici_ekle`) with role/certificate selection from initial data
- [ ] Dialog to add resource (`kaynak_ekle`) with type/role selection from initial data
- [ ] Immediate live update of calendar, user dropdown, and resource lists
