import fs from "fs";
import path from "path";

const BASE_DIR = process.cwd();

// 검사 대상 공개 파일 목록
const PUBLIC_FILES = [
  path.join(BASE_DIR, "index.html"),
  path.join(BASE_DIR, "main.js"),
  path.join(BASE_DIR, "styles.css"),
  path.join(BASE_DIR, "data", "coupons.json")
];

// 검사할 위험 시크릿 패턴 정규식
const FORBIDDEN_PATTERNS: { name: string; regex: RegExp }[] = [
  { name: "하드코딩 마스터 비밀번호 (635835)", regex: /\b635835\b/ },
  { name: "Google API Key (AIzaSy...)", regex: /AIzaSy[0-9A-Za-z-_]{33}/ },
  { name: "GitHub Personal Access Token (ghp_...)", regex: /ghp_[0-9A-Za-z]{36}/ },
  { name: "OpenAI Secret Key (sk-...)", regex: /sk-[a-zA-Z0-9]{20,}/ },
  { name: "RSA/EC Private Key", regex: /-----BEGIN [A-Z ]*PRIVATE KEY-----/ },
  { name: "AWS Secret Key", regex: /AKIA[0-9A-Z]{16}/ }
];

export function runSecretLint(): boolean {
  console.log("\n🔒 Running Public Artifact Secret Lint...");
  let leaksFound = 0;

  for (const filePath of PUBLIC_FILES) {
    if (!fs.existsSync(filePath)) continue;
    const content = fs.readFileSync(filePath, "utf-8");
    const relPath = path.relative(BASE_DIR, filePath);

    for (const pattern of FORBIDDEN_PATTERNS) {
      if (pattern.regex.test(content)) {
        console.error(`🚨 SECRET LEAK DETECTED in [${relPath}]: ${pattern.name}`);
        leaksFound++;
      }
    }
  }

  if (leaksFound === 0) {
    console.log("✅ Secret Lint Passed: 공개 클라이언트 번들 및 데이터에서 시크릿이 전혀 발견되지 않았습니다.\n");
    return true;
  } else {
    console.error(`❌ Secret Lint Failed: ${leaksFound}건의 기밀 유출이 감지되었습니다.`);
    process.exit(1);
  }
}

if (process.argv[1] === new URL(import.meta.url).pathname || process.argv[1].endsWith("secret-lint.ts")) {
  runSecretLint();
}
