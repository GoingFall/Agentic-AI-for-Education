# Web 前端已知控制台警告

开发时在浏览器控制台或审计工具中可能看到以下警告，多数来自**第三方依赖**（dash-cytoscape、dash-core-components 等），本仓库无法直接修复。

## 1. 滚轮缩放灵敏度（wheel sensitivity）

```
You have set a custom wheel sensitivity. This will make your app zoom unnaturally...
```

- **来源**：cytoscape.js（由 dash-cytoscape 使用的知识图谱库）在初始化时使用了非默认的滚轮灵敏度。
- **说明**：库内部或 react-cytoscape 设置了自定义 `wheelSensitivity`，导致 cytoscape.js 打印该提示。Dash Cytoscape 的官方 API 未暴露该选项，应用层无法覆盖。
- **影响**：仅控制台提示，不影响功能；若在不同鼠标/系统上感觉缩放异常，可关注 dash-cytoscape 后续是否支持该配置。
- **参考**：[dash-cytoscape#97](https://github.com/plotly/dash-cytoscape/issues/97)

## 2. React 废弃生命周期（componentWillMount / componentWillReceiveProps）

```
Warning: componentWillMount has been renamed...
Warning: componentWillReceiveProps has been renamed...
Please update the following components: t
```

- **来源**：react-cytoscape（dash-cytoscape 的 React 封装）中仍在使用 React 已废弃的生命周期方法，组件在压缩后显示为 `t`。
- **说明**：React 18 建议使用 `componentDidMount`、`getDerivedStateFromProps` 等替代；需依赖库升级后才能消除。
- **影响**：仅开发时控制台警告，运行行为正常；未来 React 主版本可能移除对旧生命周期的支持。
- **参考**：[React 文档 - Unsafe Lifecycles](https://reactjs.org/link/unsafe-component-lifecycles)

## 3. 表单控件 id/name 与 label 关联（审计工具）

审计工具可能报告：

- **「A form field element should have an id or name attribute」**（若干项）
- **「No label associated with a form field」**（若干项）

- **来源**：**dash-core-components**（如 `dcc.Dropdown`、`dcc.Checklist`、`dcc.Textarea` 等）内部渲染的 `<input>`/`<select>` 等，id 常挂在包装节点上，内部表单控件无 id/name；或存在多个控件（如 Checklist 的多个 checkbox），均无与 `html.Label` 的 `htmlFor` 可匹配的 id。
- **说明**：应用层无法在不修改 dash-core-components 的前提下给这些内部控件加 id/name 或正确关联 label；本应用已对部分自写 label 去掉 `htmlFor` 以避免「for 指向非表单元素」的报错。
- **影响**：仅审计/可访问性提示，不影响功能与自动填充在多数场景下的表现。
- **建议**：可忽略或通过审计工具排除；若需严格合规，需等待上游支持或考虑替代组件。

## 处理建议

- **开发/调试**：可忽略上述警告，或使用浏览器控制台的过滤功能隐藏已知来源的日志。
- **依赖升级**：定期检查 `dash-cytoscape`、`dash` 的更新说明，新版本可能已修复部分问题。
- **功能**：知识图谱 Tab 的展示与交互不受上述警告影响；表单/label 相关项不影响当前功能。
