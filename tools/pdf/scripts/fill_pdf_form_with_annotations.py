import json
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText




def transform_from_image_coords(bbox, image_width, image_height, pdf_width, pdf_height):
    """把图像坐标系（左上角原点）的边界框映射到 PDF 坐标系（左下角原点）。

    输入 bbox 形如 (left, top, right, bottom)，来自图像坐标（y 向下增加）；
    返回 (left, bottom, right, top)，供 pypdf 的 FreeText rect 使用。
    """
    x_scale = pdf_width / image_width
    y_scale = pdf_height / image_height

    left = bbox[0] * x_scale
    right = bbox[2] * x_scale

    # bbox[1] 是上边界（距顶），翻转后为 PDF 的 bottom；bbox[3] 是下边界，翻转后为 top
    bottom = pdf_height - (bbox[1] * y_scale)
    top = pdf_height - (bbox[3] * y_scale)

    return left, bottom, right, top


def transform_from_pdf_coords(bbox, pdf_height):
    """把 top-left 原点（y 向下增加）的 PDF 边界框转为 pypdf FreeText rect。

    forms.md 约定：fields.json 使用 PDF 坐标，y=0 在页面顶部、y 向下增加，
    即 bbox 形如 (left, top, right, bottom)。pypdf 的 rect 需要 bottom-left
    原点（y 向上增加），因此 y 轴需要翻转：bottom = pdf_height - bbox[3]，
    top = pdf_height - bbox[1]。
    """
    left = bbox[0]
    right = bbox[2]

    # bbox[1] 是上边界（距顶），翻转后为 rect 的 top；bbox[3] 是下边界，翻转后为 bottom
    top = pdf_height - bbox[1]
    bottom = pdf_height - bbox[3]

    return left, bottom, right, top


def fill_pdf_form(input_pdf_path, fields_json_path, output_pdf_path):
    
    with open(fields_json_path, "r") as f:
        fields_data = json.load(f)
    
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    writer.append(reader)
    
    pdf_dimensions = {}
    for i, page in enumerate(reader.pages):
        mediabox = page.mediabox
        pdf_dimensions[i + 1] = [mediabox.width, mediabox.height]
    
    annotations = []
    for field in fields_data["form_fields"]:
        page_num = field["page_number"]

        page_info = next(p for p in fields_data["pages"] if p["page_number"] == page_num)
        pdf_width, pdf_height = pdf_dimensions[page_num]

        if "pdf_width" in page_info:
            transformed_entry_box = transform_from_pdf_coords(
                field["entry_bounding_box"],
                float(pdf_height)
            )
        else:
            image_width = page_info["image_width"]
            image_height = page_info["image_height"]
            transformed_entry_box = transform_from_image_coords(
                field["entry_bounding_box"],
                image_width, image_height,
                float(pdf_width), float(pdf_height)
            )
        
        if "entry_text" not in field or "text" not in field["entry_text"]:
            continue
        entry_text = field["entry_text"]
        text = entry_text["text"]
        if not text:
            continue
        
        font_name = entry_text.get("font", "Arial")
        font_size = str(entry_text.get("font_size", 14)) + "pt"
        font_color = entry_text.get("font_color", "000000")

        annotation = FreeText(
            text=text,
            rect=transformed_entry_box,
            font=font_name,
            font_size=font_size,
            font_color=font_color,
            border_color=None,
            background_color=None,
        )
        annotations.append(annotation)
        writer.add_annotation(page_number=page_num - 1, annotation=annotation)
        
    with open(output_pdf_path, "wb") as output:
        writer.write(output)
    
    print(f"Successfully filled PDF form and saved to {output_pdf_path}")
    print(f"Added {len(annotations)} text annotations")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: fill_pdf_form_with_annotations.py [input pdf] [fields.json] [output pdf]")
        sys.exit(1)
    input_pdf = sys.argv[1]
    fields_json = sys.argv[2]
    output_pdf = sys.argv[3]
    
    fill_pdf_form(input_pdf, fields_json, output_pdf)
