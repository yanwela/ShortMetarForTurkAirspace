ShortMetarForTurkAirspace 
VATSIM ağındaki Türkiye hava sahası (LTXX) trafiğini izleyen ve ilgili meydanların güncel METAR verilerini kullanıcının isteği özelinde sunan,bir harici plugindir.

  Türkçe
· Canlı VATSIM Verisi: Türkiye hava sahasındaki (LTXX) tüm aktif kalkış ve varış trafiklerini anlık takip eder.

· Akıllı METAR Sorgulama: Trafik olan meydanların hava durumunu otomatik listeler.

· ES Modu (Overlay): EuroScope üzerinde kullanıma uygun, çerçevesiz ve şeffaf mod.

· Özet Görünüm: METAR verilerini rüzgar ve basınç (QNH) olarak sadeleştiren mod.

· Gelişmiş Filtreleme: Sadece Kalkış, sadece Varış veya Hepsi seçeneği.

· Dinamik Arayüz: Ayarlanabilir yazı boyutu, tazeleme aralığı ve "Her Zaman Üstte" (Pin) özelliği.

· Zaman Takibi: Canlı TR ve UTC saat gösterimi.

· Çift Dil: Türkçe ve İngilizce dil desteği.

   English
  
An external plugin that monitors VATSIM network traffic in Turkish airspace (LTXX) and provides up-to-date METAR data for relevant airports based on user preferences.

· Smart METAR Fetching: Automatically retrieves weather reports for active airports.

· ES Mode (Overlay): Frameless and transparent mode, perfect for use over EuroScope.

· Summary View: Simplifies METAR data to wind and pressure (QNH) info only.

· Advanced Filtering: Options for Departures only, Arrivals only, or All Airports.

· Dynamic UI: Adjustable font size, refresh intervals, and "Always-on-Top" (Pin) feature.

· Time Tracking: Live TR (Local) and UTC clock displays.

· Dual Language: Full Turkish and English support.

 Kısayollar (Shortcuts)
· ES Mode Exit: Escape (Ayarlardan değiştirilebilir / Changeable via settings).

· Drag & Move: Uygulamayı metin alanından tutarak sürükleyebilirsiniz / Drag the app from the text area.

📦 Gereksinimler (Requirements)
Python 3.x
requests
customtkinter

 Bilinen Hatalar & Geliştirme (Known Bugs & Roadmap)
🇹🇷 Türkçe
· Bug: ES Modundan çıkış yapıldığında ana arayüzün yerleşiminde (layout) kaymalar veya görsel farklılıklar oluşabiliyor.

· İyileştirme: ES modunda şeffaf pencereyi hareket ettirmek için metin alanının en kenarlarından (border kısımlarından) tutulması gerekmektedir. Orta kısımdan sürükleme hassasiyeti üzerinde çalışılıyor.


· Bug: Layout inconsistencies or visual differences may occur in the main UI when exiting ES Mode.

· Improvement: In ES Mode, the transparent window must be dragged by the edges of the textbox. Sensitivity for dragging from the center is currently being optimized.

 Geliştirici Notu (Developer Tip)
· TR: ES modundayken pencereyi hareket ettiremiyorsanız, lütfen farenizle metin kutusunun en sağ veya en sol sınırından tutarak sürüklemeyi deneyin.

· EN: If you have trouble moving the window in ES mode, please try dragging it by holding the far left or right/top or bottom edges of the textbox.
