"""
ColorUtils 테스트 모듈

색상 유틸리티 함수들의 기능을 테스트합니다.
"""

import unittest
import os
import sys

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.color_utils import ColorUtils


class TestColorUtils(unittest.TestCase):
    """ColorUtils 테스트 클래스"""
    
    def test_get_urgency_color(self):
        """긴급도별 색상 반환 테스트"""
        self.assertEqual(ColorUtils.get_urgency_color('overdue'), '#ff4444')
        self.assertEqual(ColorUtils.get_urgency_color('urgent'), '#ff8800')
        self.assertEqual(ColorUtils.get_urgency_color('warning'), '#ffcc00')
        self.assertEqual(ColorUtils.get_urgency_color('normal'), '#000000')
        
        # 잘못된 레벨은 normal 색상 반환
        self.assertEqual(ColorUtils.get_urgency_color('invalid'), '#000000')
    
    def test_get_urgency_background_color(self):
        """긴급도별 배경색 반환 테스트"""
        self.assertEqual(ColorUtils.get_urgency_background_color('overdue'), '#ffe6e6')
        self.assertEqual(ColorUtils.get_urgency_background_color('urgent'), '#fff2e6')
        self.assertEqual(ColorUtils.get_urgency_background_color('warning'), '#fffbe6')
        self.assertEqual(ColorUtils.get_urgency_background_color('normal'), '#ffffff')
    
    def test_get_completed_colors(self):
        """완료된 항목 색상 테스트"""
        colors = ColorUtils.get_completed_colors()
        
        self.assertIn('text', colors)
        self.assertIn('background', colors)
        self.assertEqual(colors['text'], '#888888')
        self.assertEqual(colors['background'], '#f5f5f5')
    
    def test_hex_to_rgb(self):
        """16진수를 RGB로 변환 테스트"""
        # 흰색
        rgb = ColorUtils.hex_to_rgb('#ffffff')
        self.assertEqual(rgb, (255, 255, 255))
        
        # 검은색
        rgb = ColorUtils.hex_to_rgb('#000000')
        self.assertEqual(rgb, (0, 0, 0))
        
        # 빨간색
        rgb = ColorUtils.hex_to_rgb('#ff0000')
        self.assertEqual(rgb, (255, 0, 0))
        
        # # 없는 경우
        rgb = ColorUtils.hex_to_rgb('ffffff')
        self.assertEqual(rgb, (255, 255, 255))
        
        # 잘못된 형식
        rgb = ColorUtils.hex_to_rgb('invalid')
        self.assertEqual(rgb, (0, 0, 0))
    
    def test_rgb_to_hex(self):
        """RGB를 16진수로 변환 테스트"""
        hex_color = ColorUtils.rgb_to_hex(255, 255, 255)
        self.assertEqual(hex_color, '#ffffff')
        
        hex_color = ColorUtils.rgb_to_hex(255, 0, 0)
        self.assertEqual(hex_color, '#ff0000')
        
        hex_color = ColorUtils.rgb_to_hex(0, 0, 0)
        self.assertEqual(hex_color, '#000000')
    
    def test_get_contrast_color(self):
        """대비 색상 계산 테스트"""
        # 밝은 배경에는 검은색 텍스트
        contrast = ColorUtils.get_contrast_color('#ffffff')
        self.assertEqual(contrast, '#000000')
        
        # 어두운 배경에는 흰색 텍스트
        contrast = ColorUtils.get_contrast_color('#000000')
        self.assertEqual(contrast, '#ffffff')
    
    def test_lighten_color(self):
        """색상 밝게 만들기 테스트"""
        # 검은색을 밝게
        lighter = ColorUtils.lighten_color('#000000', 0.5)
        self.assertNotEqual(lighter, '#000000')
        
        # 결과가 원본보다 밝은지 확인
        original_rgb = ColorUtils.hex_to_rgb('#000000')
        lighter_rgb = ColorUtils.hex_to_rgb(lighter)
        
        self.assertGreaterEqual(lighter_rgb[0], original_rgb[0])
        self.assertGreaterEqual(lighter_rgb[1], original_rgb[1])
        self.assertGreaterEqual(lighter_rgb[2], original_rgb[2])
    
    def test_darken_color(self):
        """색상 어둡게 만들기 테스트"""
        # 흰색을 어둡게
        darker = ColorUtils.darken_color('#ffffff', 0.5)
        self.assertNotEqual(darker, '#ffffff')
        
        # 결과가 원본보다 어두운지 확인
        original_rgb = ColorUtils.hex_to_rgb('#ffffff')
        darker_rgb = ColorUtils.hex_to_rgb(darker)
        
        self.assertLessEqual(darker_rgb[0], original_rgb[0])
        self.assertLessEqual(darker_rgb[1], original_rgb[1])
        self.assertLessEqual(darker_rgb[2], original_rgb[2])
    
    def test_get_urgency_style_config(self):
        """긴급도별 스타일 설정 테스트"""
        # 일반 상태
        config = ColorUtils.get_urgency_style_config('normal', False)
        self.assertIn('foreground', config)
        self.assertIn('background', config)
        self.assertIn('font', config)
        
        # 완료 상태
        config = ColorUtils.get_urgency_style_config('normal', True)
        self.assertEqual(config['foreground'], '#888888')
        self.assertIn('overstrike', config['font'])
        
        # 긴급 상태 (굵은 글씨)
        config = ColorUtils.get_urgency_style_config('urgent', False)
        self.assertIn('bold', config['font'])
    
    def test_get_accessibility_patterns(self):
        """접근성 패턴 테스트"""
        patterns = ColorUtils.get_accessibility_patterns()
        
        self.assertIn('overdue', patterns)
        self.assertIn('urgent', patterns)
        self.assertIn('warning', patterns)
        self.assertIn('normal', patterns)
        self.assertIn('completed', patterns)
        
        # 각 패턴이 문자열인지 확인
        for pattern in patterns.values():
            self.assertIsInstance(pattern, str)
    
    def test_validate_hex_color(self):
        """16진수 색상 유효성 검사 테스트"""
        # 유효한 색상들
        self.assertTrue(ColorUtils.validate_hex_color('#ffffff'))
        self.assertTrue(ColorUtils.validate_hex_color('#000000'))
        self.assertTrue(ColorUtils.validate_hex_color('#ff0000'))
        
        # 무효한 색상들
        self.assertFalse(ColorUtils.validate_hex_color('ffffff'))   # # 없음
        self.assertFalse(ColorUtils.validate_hex_color('#fff'))     # 3자리
        self.assertFalse(ColorUtils.validate_hex_color('#gggggg'))  # 잘못된 문자
        self.assertFalse(ColorUtils.validate_hex_color(''))         # 빈 문자열
        self.assertFalse(ColorUtils.validate_hex_color(None))       # None


if __name__ == '__main__':
    unittest.main()