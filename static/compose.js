var myCodeMirror = CodeMirror.fromTextArea(document.getElementById("myTextArea"), {
    mode: "python",
    lineNumbers: true,
    indentUnit: 4,
    matchBrackets: true,
    autoCloseBrackets: true
});
function change_mode()
{
    let mode = document.getElementById("mode").value;
    myCodeMirror.setOption("mode", mode);
}