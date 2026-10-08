# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

from graphrag_input import InputConfig, InputType, create_input_reader
from graphrag_storage import StorageConfig, create_storage


async def test_jsonl_loader_one_file_multiple_objects():
    config = InputConfig(
        type=InputType.JsonLines,
        file_pattern=".*\\.jsonl$",
    )
    storage = create_storage(
        StorageConfig(
            base_dir="tests/unit/indexing/input/data/one-jsonl",
        )
    )
    reader = create_input_reader(config, storage)
    documents = await reader.read_files()
    assert len(documents) == 3
    assert documents[0].title == "input.jsonl (0)"
    assert documents[0].raw_data == {
        "title": "Hello",
        "text": "Hi how are you today?",
    }
    assert documents[1].title == "input.jsonl (1)"


async def test_jsonl_loader_one_file_with_title():
    config = InputConfig(
        type=InputType.JsonLines,
        title_column="title",
    )
    storage = create_storage(
        StorageConfig(
            base_dir="tests/unit/indexing/input/data/one-jsonl",
        )
    )
    reader = create_input_reader(config, storage)
    documents = await reader.read_files()
    assert len(documents) == 3
    assert documents[0].title == "Hello"


async def test_jsonl_loader_skips_blank_and_invalid_rows():
    config = InputConfig(
        type=InputType.JsonLines,
        title_column="title",
    )
    storage = create_storage(
        StorageConfig(
            base_dir="tests/unit/indexing/input/data/jsonl-with-invalid-and-blank-lines",
        )
    )
    reader = create_input_reader(config, storage)
    documents = await reader.read_files()

    assert len(documents) == 3
    assert [document.title for document in documents] == ["Hello", "Goodbye", "Adios"]


async def test_jsonl_loader_keeps_rows_with_unicode_line_separators(tmp_path):
    ls, nel, ps = chr(0x2028), chr(0x85), chr(0x2029)
    rows = [
        f'{{"title": "a", "text": "x{ls}y"}}',
        f'{{"title": "b", "text": "x{nel}y{ps}z"}}',
        '{"title": "c", "text": "plain"}',
    ]
    (tmp_path / "input.jsonl").write_text(
        "\r\n".join(rows) + "\r\n", encoding="utf-8", newline=""
    )
    config = InputConfig(type=InputType.JsonLines, title_column="title")
    storage = create_storage(StorageConfig(base_dir=str(tmp_path)))
    reader = create_input_reader(config, storage)
    documents = await reader.read_files()

    assert [document.title for document in documents] == ["a", "b", "c"]
    assert documents[0].text == f"x{ls}y"
    assert documents[1].text == f"x{nel}y{ps}z"
