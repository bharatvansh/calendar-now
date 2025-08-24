import os
from pathlib import Path

PNG_SIZES = [16, 24, 32, 48, 64, 128, 256]

def convert_svg_to_pngs(svg_path: Path, out_stem: str, out_dir: Path):
	"""Convert an SVG to multiple PNG sizes using Qt's SVG renderer.
	This avoids external native dependencies on Windows.
	"""
	from PyQt5.QtSvg import QSvgRenderer
	from PyQt5.QtGui import QImage, QPainter
	from PyQt5.QtCore import QSize
	from PyQt5.QtWidgets import QApplication

	# Ensure a Qt application exists
	app = QApplication.instance() or QApplication([])

	out_dir.mkdir(parents=True, exist_ok=True)
	renderer = QSvgRenderer(str(svg_path))
	if not renderer.isValid():
		raise RuntimeError(f"Invalid SVG: {svg_path}")

	png_paths = []
	for size in PNG_SIZES:
		image = QImage(size, size, QImage.Format_ARGB32)
		image.fill(0)
		painter = QPainter(image)
		renderer.render(painter)
		painter.end()
		out_path = out_dir / f"{out_stem}-{size}.png"
		image.save(str(out_path))
		png_paths.append(out_path)
	# also export a default name without suffix for app usage (32px)
	default_png = out_dir / f"{out_stem}.png"
	if not default_png.exists() and (out_dir / f"{out_stem}-32.png").exists():
		(out_dir / f"{out_stem}-32.png").replace(default_png)
	return png_paths

def make_ico_from_pngs(png_paths, ico_path: Path):
	from PIL import Image
	# Open images and ensure RGBA
	images = [Image.open(p).convert('RGBA') for p in png_paths if p.exists()]
	if not images:
		raise RuntimeError("No PNGs found to build ICO")
	# Save ICO with multiple sizes
	sizes = [(img.width, img.height) for img in images]
	# Use the first as base
	base = images[0]
	base.save(ico_path, format='ICO', sizes=sizes)

def main():
	project_root = Path(__file__).parent
	icons_dir = project_root / 'resources' / 'icons'
	icons_dir.mkdir(parents=True, exist_ok=True)

	# Convert tray icon
	tray_svg = icons_dir / 'tray_icon.svg'
	if tray_svg.exists():
		tray_pngs = convert_svg_to_pngs(tray_svg, 'tray_icon', icons_dir)
		make_ico_from_pngs(tray_pngs, icons_dir / 'tray_icon.ico')
		print("Converted tray_icon.svg -> PNGs and ICO")
	else:
		print("tray_icon.svg not found, skipping")

	# Convert app icon (fall back to tray if not present)
	app_svg = icons_dir / 'app_icon.svg'
	if app_svg.exists():
		app_pngs = convert_svg_to_pngs(app_svg, 'app_icon', icons_dir)
		make_ico_from_pngs(app_pngs, icons_dir / 'app_icon.ico')
		print("Converted app_icon.svg -> PNGs and ICO")
	elif tray_svg.exists():
		# create app icon copies from tray
		for p in icons_dir.glob('tray_icon-*.png'):
			target = icons_dir / p.name.replace('tray_icon-', 'app_icon-')
			if target.exists():
				target.unlink()
			p.replace(target)
		if (icons_dir / 'tray_icon.ico').exists():
			(icons_dir / 'tray_icon.ico').replace(icons_dir / 'app_icon.ico')
		if (icons_dir / 'tray_icon.png').exists():
			(icons_dir / 'tray_icon.png').replace(icons_dir / 'app_icon.png')
		print("Created app icon from tray icon")
	else:
		print("No SVG icons found to convert")

if __name__ == '__main__':
	main()
