# haoge 越狱源

源地址：https://hech666.github.io/

## 上传软件包

1. 打开仓库的 `debs` 目录，选择 **Add file → Upload files**。
2. 上传你有权分发的 `.deb` 文件，提交到 main 分支。
3. 在 Actions 查看 Publish APT repository，成功后刷新软件源。

自动化只负责生成 APT 索引和发布网站，不会编译、修改或转换安装包。初始源为空。
GitHub 单个文件硬限制为 100 MiB，建议 deb 小于 50 MiB。不要提交付费盗版包、凭证或隐私数据。
不同越狱环境请上传对应架构的包；不要以相同 Package + Version + Architecture 上传不同内容。

## 结构

- debs/: 安装包
- scripts/build.py: 用 dpkg-deb 读取 control，生成 Packages、压缩索引、Release 和哈希
- site/index.html: 主页
- .github/workflows/pages.yml: GitHub Pages 发布流水线

Pages 设置必须为 GitHub Actions。本地测试：`python3 scripts/build.py`（需要 dpkg-deb）。生成目录 public 不必提交。

这是面向越狱软件管理器的未签名 HTTPS 平面源，不包含 GPG 签名；桌面 APT 默认可能拒绝。只分发你拥有或获授权的软件。
