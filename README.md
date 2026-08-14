# CrossSectAI: Cross-Section Parameter Extraction using Artificial Intelligence

Bridges are vital components of transportation infrastructure, but many, particularly in countries like Germany, urgently require maintenance due to aging. Digital methods such as Building Information Modeling (BIM) and Digital Twinning support efficient maintenance planning. However, these methods rely heavily on accurate digital models, which are often unavailable for existing bridges. Consequently, digital reconstruction from construction drawings becomes necessary. Automating this reconstruction significantly accelerates the adoption of BIM and Digital Twinning for bridge maintenance.

This repository provides an implementation of the end-to-end pipeline introduced in our paper. The pipeline automatically extracts bridge cross-section geometries from existing construction drawings. The process uses YOLOv8 to detect cross-sections and the Segment Anything Model (SAM) to generate precise pixel-wise masks. These masks feed into a global optimization algorithm that matches parametric templates to the masks by minimizing a custom loss function, thus deriving accurate geometric parameters.

---

## Usage

### Setup

See below for quickstart installation and usage examples. 

<details open>
<summary>Install</summary>

The project uses `pipenv` to manage dependencies. To set up the environment, run:

```bash
pip install pipenv
pipenv install
```

The pre-trained YOLOv8 weights are already included in the directory of this repository. To use SAM, manually download the checkpoint from the [official repository](https://github.com/facebookresearch/segment-anything/blob/main/README.md#model-checkpoints).

Ensure that the correct paths to the model weights are set in the configuration file (`default.yaml`):
</details>

<details open>
<summary>Usage</summary>

You can use CrossSectAI directly from the Command Line Interface:

```bash
pipenv run python main.py -i <input_path> -o <output_dir> [-c <config_path>]
```

The command accepts the following arguments:

- `-i`, `--input`   **(required)** Path to a PNG image or a folder containing PNG images.

- `-o`, `--output`  **(required)** Path to the output directory.

- `-c`, `--config`  Path to the YAML configuration file. Defaults to `default.yaml`.


### Example

To run the included example, execute the following command from the project root:

```bash
pipenv run python main.py -i examples/img.png -o ./
```

</details>


### GeoJSON export

For each processed image, a `<image_stem>.geojson` file is written to the output directory — this is the only output the pipeline produces. It contains a `FeatureCollection` of `Polygon` features, one per detected cross-section, in image-pixel coordinates. Each polygon's coordinates are centered on that polygon's own bounding-box center (i.e. translated so the box center maps to `(0, 0)`), rather than being left relative to the image's top-left corner. Each feature's `properties` include an `id`, the template `name` (e.g. `"Slab Girder"`), the fitted-polygon `color` (from `default.yaml`), the absolute image-pixel `center` the polygon's coordinates are relative to, and a `created_at` timestamp.



## License

This software is licensed under [MIT License](/LICENSE).
