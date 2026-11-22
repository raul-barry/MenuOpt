import 'package:flutter_test/flutter_test.dart';
import 'package:menuopt_mobile/core/api_client.dart';

void main() {
  group('ApiClient.buildCandidateUrls', () {
    test('release usa HTTPS de Render y no incluye hosts locales', () {
      final candidates = ApiClient.buildCandidateUrls(
        release: true,
        configuredBaseUrl: 'https://menuopt-api.onrender.com',
      );

      expect(candidates, ['https://menuopt-api.onrender.com']);
      expect(
        candidates.every((url) => Uri.parse(url).scheme == 'https'),
        isTrue,
      );
    });

    test('release ignora una URL local configurada por error', () {
      final candidates = ApiClient.buildCandidateUrls(
        release: true,
        configuredBaseUrl: 'http://10.0.2.2:8000',
      );

      expect(candidates, ['https://menuopt-api.onrender.com']);
    });

    test('debug conserva los candidatos locales para desarrollo', () {
      final candidates = ApiClient.buildCandidateUrls(
        release: false,
        configuredBaseUrl: '',
      );

      expect(candidates, contains('http://192.168.0.4:8000'));
      expect(candidates, contains('http://10.0.2.2:8000'));
    });
  });
}
