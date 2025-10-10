// =================================================================
// 最终版 JSX 模板 v2 (支持自定义文件名前缀)
// =================================================================

try {
    $.sleep(3000); 

    // --- 配置区 ---
    var ACTION_SET_NAME = "默认动作";
    var ACTION_NAME = "移除背景";
    // --- 占位符 (由Python填充) ---
    var FILENAME_PREFIX = "PLACEHOLDER_PREFIX";
    var inputFolder = new Folder("PLACEHOLDER_INPUT");
    var outputFolder = new Folder("PLACEHOLDER_OUTPUT");

    // --- 辅助函数：数字补零 ---
    function pad(num, size) {
        var s = num + "";
        while (s.length < size) s = "0" + s;
        return s;
    }

    // --- 核心处理逻辑 ---
    if (!outputFolder.exists) {
        outputFolder.create();
    }
    var fileList = inputFolder.getFiles("*.png");
    if (fileList.length > 0) {
        // 对文件列表进行排序，确保处理顺序正确
        fileList.sort();
        for (var i = 0; i < fileList.length; i++) {
            var doc = open(fileList[i]);
            app.doAction(ACTION_NAME, ACTION_SET_NAME);
            
            var pngOptions = new PNGSaveOptions();
            pngOptions.compression = 9;
            pngOptions.interlaced = false;

            // 使用新的命名规则：前缀 + 补零的序号
            var newName = FILENAME_PREFIX + "_" + pad(i + 1, 4) + ".png";
            var outputFile = new File(outputFolder + "/" + newName);
            
            doc.saveAs(outputFile, pngOptions, true, Extension.LOWERCASE);
            doc.close(SaveOptions.DONOTSAVECHANGES);
        }
    }

    // --- 创建信号文件 ---
    var scriptFile = new File($.fileName);
    var projectFolder = scriptFile.parent;
    var signalFile = new File(projectFolder + "/photoshop_done.tmp");
    signalFile.open("w");
    signalFile.write("done");
    signalFile.close();

} catch(e) {
    var scriptFile = new File($.fileName);
    var projectFolder = scriptFile.parent;
    var signalFile = new File(projectFolder + "/photoshop_done.tmp");
    signalFile.open("w");
    signalFile.write("error: " + e.message);
    signalFile.close();
}