/**
 * @license Copyright (c) 2003-2015, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
	config.extraPlugins = 'pastebase64';
	config.extraPlugins = 'uploadimage';
	config.extraPlugins = 'uploadwidget';
	config.extraPlugins = 'widget';
	config.extraPlugins = 'lineutils';
	config.extraPlugins = 'filetools';
	config.extraPlugins = 'notificationaggregator';
	config.extraPlugins = 'notification';
	config.extraPlugins = 'toolbar';
	config.extraPlugins = 'button';
	config.extraPlugins = 'imagepaste';
};

CKEDITOR.replace( 'editor1', {
  extraPlugins: 'imageuploader'
});

CKEDITOR.editorConfig = function( config ) {
  config.extraPlugins = 'imageuploader';
};

