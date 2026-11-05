
$so = 'C:\Program Files\LibreOffice\program\soffice.exe'
$dir = 'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'
Get-ChildItem $dir -Filter '*.docx' | Where-Object { $_.Name -match '_(上|中|下)卷\.docx$' } | Sort-Object Name | ForEach-Object {
  Start-Process -FilePath $so -ArgumentList @('--headless','--norestore','-env:UserInstallation=file:///C:/Temp/lo_profile_six','--convert-to','pdf','--outdir',$dir,$_.FullName) -Wait -NoNewWindow
  Write-Output ('converted ' + $_.Name)
}
'ALLDONE'
