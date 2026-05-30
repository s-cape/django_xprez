/**
 * Custom CKEditor 5 balloon block build for xprez.
 *
 * Uses the umbrella `ckeditor5` package (new installation method). The editor
 * class is exposed as the global `BalloonBlockEditor` consumed by
 * static/ck_editor/js/ck_editor_widget.js.
 */
import {
	BalloonEditor,
	Autoformat,
	BlockQuote,
	BlockToolbar,
	Bold,
	Essentials,
	Heading,
	Image,
	ImageCaption,
	ImageStyle,
	ImageToolbar,
	ImageUpload,
	ImageTextAlternative,
	Italic,
	Link,
	LinkImage,
	List,
	MediaEmbed,
	Paragraph,
	PasteFromOffice,
	SimpleUploadAdapter,
	Table,
	TableToolbar,
	TextTransformation,
} from "ckeditor5";
import "ckeditor5/ckeditor5.css";

class BalloonBlockEditor extends BalloonEditor {}

BalloonBlockEditor.builtinPlugins = [
	Autoformat,
	BlockQuote,
	BlockToolbar,
	Bold,
	Essentials,
	Heading,
	Image,
	ImageCaption,
	ImageStyle,
	ImageToolbar,
	ImageUpload,
	ImageTextAlternative,
	Italic,
	Link,
	LinkImage,
	List,
	MediaEmbed,
	Paragraph,
	PasteFromOffice,
	SimpleUploadAdapter,
	Table,
	TableToolbar,
	TextTransformation,
];

window.BalloonBlockEditor = BalloonBlockEditor;
