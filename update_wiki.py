from argparse import ArgumentParser
from pathlib import Path
from typing import Any

import filetype
from arclet.alconna import TextFormatter
from meme_generator import get_memes
from meme_generator.meme import Meme
from pil_utils import BuildImage


class Generator:
    def __init__(self, memes: list[Meme], root_path: Path) -> None:
        self.memes = memes
        self.root_path = root_path
        self.image_path = root_path / "images"
        self.thumb_path = root_path / "thumbs"
        self.md_path = root_path / "表情列表.md"

    def generate_image(self, meme: Meme, name: str, args: dict[str, Any]) -> None:
        for path in self.image_path.iterdir():
            if name == path.stem:
                return

        result = meme.generate_preview(args=args)
        content = result.getvalue()
        ext = filetype.guess_extension(content)
        filename = f"{name}.{ext}"
        with open(self.image_path / filename, "wb") as f:
            f.write(content)

        img = BuildImage.open(result)
        if img.width > 150:
            result_resized = img.convert("RGBA").resize_width(150).save_jpg()
        else:
            result_resized = img.save_jpg()
        filename_resized = f"{name}.jpg"
        with open(self.thumb_path / filename_resized, "wb") as f:
            f.write(result_resized.getvalue())

    def generate_images(self):
        for meme in self.memes:
            self.generate_image(meme, meme.key, {})
            if args := meme.params_type.args_type:
                if examples := args.args_examples:
                    for i, example in enumerate(examples):
                        self.generate_image(
                            meme,
                            f"{meme.key}_instance{i}",
                            example.model_dump(),
                        )

    def arg_info(self, name: str, info: dict[str, Any]) -> str:
        text = (
            f"    - `{name}`\n"
            f"        - 描述：{info.get('description', '')}\n"
            f"        - 类型：`{info.get('type', '')}`\n"
            f"        - 默认值：`{info.get('default', '')}`"
        )
        if enum := info.get("enum", []):
            assert isinstance(enum, list)
            text += f"\n        - 可选值：{'、'.join([f'`{e}`' for e in enum])}"
        return text

    def image_doc(self, name: str) -> str:
        image_path = Path()
        thumb_path = Path()
        for path in self.image_path.iterdir():
            if name == path.stem:
                image_path = path.relative_to(self.root_path)
        for path in self.thumb_path.iterdir():
            if name == path.stem:
                thumb_path = path.relative_to(self.root_path)
        return f"[![]({thumb_path})]({image_path})"

    def meme_doc(self, meme: Meme) -> str:
        keywords = "、".join([f"`{keyword}`" for keyword in meme.keywords])
        shortcuts = "、".join(
            [f'"{shortcut.humanized or shortcut.key}"' for shortcut in meme.shortcuts]
        )
        tags = "、".join([f'"{tag}"' for tag in sorted(meme.tags)])

        image_num = f"`{meme.params_type.min_images}`"
        if meme.params_type.max_images > meme.params_type.min_images:
            image_num += f" ~ `{meme.params_type.max_images}`"

        text_num = f"`{meme.params_type.min_texts}`"
        if meme.params_type.max_texts > meme.params_type.min_texts:
            text_num += f" ~ `{meme.params_type.max_texts}`"

        default_texts = (
            f"{', '.join([f'`{text}`' for text in meme.params_type.default_texts])}"
        )

        if args := meme.params_type.args_type:
            model = args.args_model
            properties: dict[str, dict[str, Any]] = (
                model.model_json_schema().get("properties", {}).copy()
            )
            properties.pop("user_infos")
            args_info = "\n" + "\n".join(
                [self.arg_info(name, info) for name, info in properties.items()]
            )
        else:
            args_info = ""

        parser_info = ""
        if args_type := meme.params_type.args_type:
            formater = TextFormatter()
            for option in args_type.parser_options:
                opt = option.option()
                alias_text = (
                    " ".join(opt.requires)
                    + (" " if opt.requires else "")
                    + "│".join(sorted(opt.aliases, key=len))
                )
                parser_info += (
                    f"    - {alias_text}{opt.separators[0]}"
                    f"{formater.parameters(opt.args)} {opt.help_text}\n"
                )

        preview_image = ""
        if args := meme.params_type.args_type:
            if examples := args.args_examples:
                preview_image = "\n\n".join(
                    [
                        f"> 参数：{example.model_dump_json(exclude={'user_infos'})}\n\n"
                        + self.image_doc(meme.key + f"_instance{i}")
                        for i, example in enumerate(examples)
                    ]
                )
        if not preview_image:
            preview_image = self.image_doc(meme.key)

        return (
            f"## {meme.key}\n\n"
            + f"- 关键词：{keywords}\n"
            + (f"- 快捷指令：{shortcuts}\n" if shortcuts else "")
            + (f"- 标签：{tags}\n" if tags else "")
            + f"- 需要图片数目：{image_num}\n"
            + f"- 需要文字数目：{text_num}\n"
            + (f"- 默认文字：[{default_texts}]\n" if default_texts else "")
            + (f"- 其他参数：{args_info}\n" if args_info else "")
            + (f"- 其他参数（命令行选项）：\n{parser_info}\n" if parser_info else "")
            + "- 预览：（点击图片查看原图）\n\n"
            + f"{preview_image}"
        )

    def generate_toc(self):
        return "\n".join(
            f"{i}. [{meme.key} ({'/'.join(meme.keywords)})](#{meme.key})"
            for i, meme in enumerate(self.memes, start=1)
        )

    def generate_doc(self):
        doc = "以下为表情的关键词、所需参数等信息及表情预览\n\n按照表情的 `key` 排列\n\n\n"
        doc += self.generate_toc()
        doc += "\n\n\n"
        doc += "\n\n".join(self.meme_doc(meme) for meme in self.memes)
        doc += "\n"
        with open(self.md_path, "w") as f:
            f.write(doc)

    def generate(self) -> None:
        self.image_path.mkdir(parents=True, exist_ok=True)
        self.thumb_path.mkdir(parents=True, exist_ok=True)
        self.generate_images()
        self.generate_doc()


def main():
    parser = ArgumentParser()
    parser.add_argument("path")
    namespace = parser.parse_args()

    memes = get_memes()
    memes.sort(key=lambda meme: meme.key)

    root_path = Path(namespace.path)

    generator = Generator(memes, root_path)
    generator.generate()


if __name__ == "__main__":
    main()
