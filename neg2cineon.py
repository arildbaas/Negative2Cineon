import rawpy
import numpy as np
import imageio
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
from skimage.transform import resize

epsilon = 1e-4  # Small value to avoid log(0) or divide-by-zero

COLORSPACE_MAP = {
    "raw": rawpy.ColorSpace.raw,
    "sRGB": rawpy.ColorSpace.sRGB,
    "Adobe": rawpy.ColorSpace.Adobe,
    "Wide": rawpy.ColorSpace.Wide,
    "ProPhoto": rawpy.ColorSpace.ProPhoto,
    "XYZ": rawpy.ColorSpace.XYZ,
    "ACES": rawpy.ColorSpace.ACES,
    "P3D65": rawpy.ColorSpace.P3D65,
    "Rec2020": rawpy.ColorSpace.Rec2020
}


def estimate_film_base(image, percentile=2.0):
    grayscale = np.mean(image, axis=2)
    threshold = np.percentile(grayscale, percentile)
    mask = grayscale <= threshold
    return np.mean(image[mask], axis=0)


def pick_white_balance_point(image):
    scale = 0.25
    h, w = image.shape[:2]
    small_h, small_w = int(h * scale), int(w * scale)
    small_image = resize(image, (small_h, small_w), preserve_range=True, anti_aliasing=True)
    small_image = np.clip(small_image, 0, 1)

    coords = []

    def onclick(event):
        if event.xdata and event.ydata:
            x_scaled = int(event.xdata / scale)
            y_scaled = int(event.ydata / scale)
            coords.append((x_scaled, y_scaled))
            print(f"Selected point at: ({x_scaled}, {y_scaled})")
            plt.close()

    fig, ax = plt.subplots()
    ax.imshow(small_image)
    plt.title("Click on the orange mask to white-balance")
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

    if coords:
        x, y = coords[0]
        return image[y, x]
    else:
        raise RuntimeError("No point was selected.")


def debayer_and_extract_channel(path: Path, channel_index: int, color_space="ProPhoto"):
    with rawpy.imread(str(path)) as raw:
        rgb = raw.postprocess(
            gamma=(1, 1),
            no_auto_bright=True,
            output_bps=16,
            use_camera_wb=False,
            output_color=COLORSPACE_MAP[color_space]
        )
    lin_rgb = rgb.astype(np.float32) / 65535.0
    return lin_rgb[..., channel_index]


def merge_trichromatic_images(paths, color_space):
    assert len(paths) == 3, "Trichromatic mode requires exactly 3 RAW files"
    red = debayer_and_extract_channel(paths[0], 0, color_space)
    green = debayer_and_extract_channel(paths[1], 1, color_space)
    blue = debayer_and_extract_channel(paths[2], 2, color_space)
    return np.stack((red, green, blue), axis=2)


def process_negative_to_cineon(raw_paths, exposure=1.0, color_space="ProPhoto", pick_white_balance=False):
    if len(raw_paths) == 3:
        print("Entering trichromatic mode...")
        lin_rgb = merge_trichromatic_images(raw_paths, color_space)
        lin_rgb *= exposure
        lin_rgb = np.clip(lin_rgb, epsilon, 1.0)

        if pick_white_balance:
            film_base = pick_white_balance_point(lin_rgb)
        else:
            film_base = estimate_film_base(lin_rgb)

        gains = np.mean(film_base) / film_base
        balanced_rgb = lin_rgb * gains
        balanced_rgb = np.clip(balanced_rgb, epsilon, 1.0)

        density = -np.log10(balanced_rgb)
        density = np.clip(density - 0.19, 0.0, None)

        cineon_code = 95.0 + 500.0 * density
        cineon_code = np.clip(cineon_code, 95.0, 1023.0)
        cineon_16bit = (cineon_code / 1023.0 * 65535.0).astype(np.uint16)

        output_path = raw_paths[0].with_name(raw_paths[0].stem + "_trichromatic_cineon.tiff")
        imageio.imwrite(str(output_path), cineon_16bit, format='TIFF')
        print(f"Saved Cineon TIFF to {output_path}")

    elif len(raw_paths) == 1:
        process_single_file(raw_paths[0], exposure, color_space, pick_white_balance)

    else:
        raise ValueError("You must provide either 1 or exactly 3 RAW files for trichromatic mode.")


def process_single_file(raw_path: Path, exposure=1.0, color_space="ProPhoto", pick_white_balance=False):
    output_path = raw_path.with_name(raw_path.stem + "_cineon.tiff")

    if color_space not in COLORSPACE_MAP:
        raise ValueError(f"Invalid color space '{color_space}'. Choose from: {', '.join(COLORSPACE_MAP.keys())}")

    with rawpy.imread(str(raw_path)) as raw:
        rgb = raw.postprocess(
            gamma=(1, 1),
            no_auto_bright=True,
            output_bps=16,
            use_camera_wb=False,
            output_color=COLORSPACE_MAP[color_space]
        )

    lin_rgb = rgb.astype(np.float32) / 65535.0
    lin_rgb *= exposure
    lin_rgb = np.clip(lin_rgb, epsilon, 1.0)

    if pick_white_balance:
        film_base = pick_white_balance_point(lin_rgb)
    else:
        film_base = estimate_film_base(lin_rgb)

    gains = np.mean(film_base) / film_base
    balanced_rgb = lin_rgb * gains
    balanced_rgb = np.clip(balanced_rgb, epsilon, 1.0)

    density = -np.log10(balanced_rgb)
    density = np.clip(density - 0.19, 0.0, None)

    cineon_code = 95.0 + 500.0 * density
    cineon_code = np.clip(cineon_code, 95.0, 1023.0)
    cineon_16bit = (cineon_code / 1023.0 * 65535.0).astype(np.uint16)

    imageio.imwrite(str(output_path), cineon_16bit, format='TIFF')
    print(f"Saved Cineon TIFF to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert RAW negative(s) to Cineon-style TIFF.")
    parser.add_argument("--exposure", type=float, default=1.0, help="Exposure multiplier (default: 1.0)")
    parser.add_argument("--color-space", type=str, default="ProPhoto", choices=COLORSPACE_MAP.keys(),
                        help="Output color space (default: ProPhoto)")
    parser.add_argument("--pick-wb", action="store_true", help="Enable GUI to pick white balance point manually")
    parser.add_argument("input_raws", type=Path, nargs="+", help="One or three RAW input file(s)")
    args = parser.parse_args()

    process_negative_to_cineon(args.input_raws, exposure=args.exposure,
                               color_space=args.color_space, pick_white_balance=args.pick_wb)


if __name__ == "__main__":
    main()
