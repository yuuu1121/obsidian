module.exports = async (tp) => {
    const filePath = app.vault.getAbstractFileByPath(tp.file.path);
    if (!filePath) return;

    // YAML 태그 가져오기
    const metaData = await app.plugins.plugins["metaedit"].api.getMetadata(tp.file.path);
    if (!metaData || !metaData.tags || metaData.tags.length === 0) return;

    // 첫 번째 태그의 경로로 설정 (예: Study/OpenCV -> Study_OpenCV 폴더)
    let tagPath = metaData.tags[0].replace(/\//g, "_"); // '/'는 폴더 구분자로 충돌할 수 있어 '_'로 변경
    const newFolder = tagPath; 

    // 새 경로 설정 및 이동
    const newFilePath = newFolder + "/" + tp.file.title + ".md";
    await app.fileManager.renameFile(filePath, newFilePath);
};
