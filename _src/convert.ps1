
$so = 'C:\Program Files\LibreOffice\program\soffice.exe'
$out = (Get-Location).Path + '\_build'
$pdfdir = (Get-Location).Path + '\_pdf'
New-Item -ItemType Directory -Force -Path $pdfdir | Out-Null
Get-ChildItem '.\_build\0*.docx' | Sort-Object Name | ForEach-Object {
  $src = $_.FullName
  $args = @('--headless','--norestore','-env:UserInstallation=file:///C:/Temp/lo_profile_conv','--convert-to','pdf','--outdir',$out,$src)
  Start-Process -FilePath $so -ArgumentList $args -Wait -NoNewWindow
  Write-Output ('converted ' + $_.Name)
}
'ALLDONE'
