"""uv run --with pytest pytest scripts/test_phrase_vocab.py"""

from phrase_vocab import THAI_JOINER, clean, merge_overlaps, prune_subphrases


def test_prune_drops_covered_subphrase_only():
    counts = {"siti nurhaliza": 100, "siti": 300, "nurhaliza konsert": 30, "siti nurhaliza konsert": 90}
    pruned = prune_subphrases(counts)
    assert "siti nurhaliza" not in pruned  # 90 >= 0.8 * 100
    assert "siti nurhaliza konsert" in pruned
    assert "siti" in pruned  # 90 < 0.8 * 300


def test_merge_keeps_one_window_of_a_long_name():
    # "datuk seri anwar ibrahim lawat pulau pinang" (7 từ) bị cắt thành cửa sổ 4 từ
    counts = {
        "datuk seri anwar ibrahim": 100,
        "seri anwar ibrahim lawat": 95,
        "anwar ibrahim lawat pulau": 92,
        "ibrahim lawat pulau pinang": 90,
        "harga minyak naik lagi": 40,  # cụm khác, không chồng
    }
    merged = merge_overlaps(counts)
    assert merged == {"datuk seri anwar ibrahim": 100, "harga minyak naik lagi": 40}


def test_merge_does_not_join_windows_with_different_counts():
    counts = {"promo shopee besar": 100, "shopee besar besaran": 10}
    assert merge_overlaps(counts) == counts


def test_thai_phrases_use_invisible_joiner():
    j = THAI_JOINER
    # "ร้านเจ๊ไฝ" = ร้าน|เจ๊|ไฝ (3 từ): 2 mảnh 2 từ bị cụm 3 từ phủ hết nên bị tỉa; cụm khác giữ nguyên
    counts = {f"ร้าน{j}เจ๊{j}ไฝ": 100, f"ร้าน{j}เจ๊": 100, f"เจ๊{j}ไฝ": 100, f"คิว{j}นาน": 50}
    assert prune_subphrases(counts) == {f"ร้าน{j}เจ๊{j}ไฝ": 100, f"คิว{j}นาน": 50}


def test_clean_runs_both_steps():
    counts = {"a b c d": 50, "b c d e": 48, "a b c": 55, "x y": 7}
    assert clean(counts) == {"a b c d": 50, "x y": 7}
