# Negative2Cineon

**Convert RAW scans of photographic film negatives into Cineon-style log-encoded 16-bit TIFFs**  
Supports both single-shot scanning and **trichromatic capture workflows** for high-fidelity color reproduction.

---

Scanning color negatives is hard.

Most scanning software (or even RAW converters) applies **sRGB** output transforms by default. This:
- Clips highlights and shadows
- Destroys film color fidelity
- Makes color grading and restoration difficult

**Negative2Cineon** is a minimal command-line utility that processes RAW files with:
- **Linear gamma**
- Optional **manual white balancing**
- Custom **wide gamut color spaces** like ProPhoto, ACES, Rec2020, etc.
- Support for **trichromatic capture** (three separate filtered exposures for Red, Green, and Blue)

This tool provides high-quality log-encoded TIFFs that can be finished in your grading software with full tonal and color control.

---

## Features

- Converts RAW camera files (e.g., `.ARW`, `.CR2`) into 16-bit Cineon-style TIFFs
- Optional manual white balance selection via GUI
- Supports **trichromatic input**: three RAWs captured separately through R/G/B filters
- Customizable output color spaces:
  - `ProPhoto` (default)
  - `ACES`, `P3D65`, `Rec2020`, and more
- Linear gamma debayering with no auto-exposure adjustments
- Simple and lightweight command-line interface

---

## Installation

Dependencies

- rawpy
- numpy
- imageio
- matplotlib
- scikit-image
- Python >= 3.8

Command-Line Usage

python convert_negative.py [options] input_raw [...]

Arguments
input_raw [...]
One or more RAW image files:
1 RAW file → processed normally
3 RAW files → processed in trichromatic mode (Red, Green, Blue channels)
2 RAW files → invalid input (error)
Optional Flags
--exposure <float>
Multiplier applied to linear image data before log conversion
(Default: 1.0)
--color-space <name>
Output color space for the processed TIFF
(Options: raw, sRGB, Adobe, Wide, ProPhoto, XYZ, ACES, P3D65, Rec2020)
(Default: ProPhoto)
--pick-wb
Launches a small GUI window to manually select a white balance point on the image.
Useful when scanning orange-masked color negatives.
Examples

Convert a single RAW file
python convert_negative.py my_negative.ARW
Apply exposure and choose color space
```python convert_negative.py --exposure 1.3 --color-space ACES my_negative.CR2```
Enable manual white balance picker
```python convert_negative.py --pick-wb my_negative.ARW```
Trichromatic capture (3 filtered RAWs: R, G, B)
```python convert_negative.py red.ARW green.ARW blue.ARW```

No extra flag required
Channel assignment is based on file order:
- 1st = Red
- 2nd = Green
- 3rd = Blue
  
The processed image is saved as a 16-bit TIFF in the same folder as the input file(s).

- Single-file mode: my_negative_cineon.tiff
- Trichromatic mode: red_trichromatic_cineon.tiff

The output is Log-encoded using a Cineon-style density curve, and you are expected to perform final adjustments:
- Normalize black and white points
- Apply contrast curves
- Optional LUT mapping to Rec.709, etc.
- Development Roadmap

Coming soon:

 - Automatic film base estimation and normalization
 - Basic highlight/shadow auto-level adjustment
 - Film scan “lift” curves to emulate scanner tone response
 - Cineon-to-video preview transforms
   
MIT License – free to use, modify, and distribute.
