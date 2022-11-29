/**
 * @copyright Japanese woodblock palette: https://lospec.com/palette-list/japanese-woodblock
 * @copyright CSS filters: https://codepen.io/sosuke/pen/Pjoqqp
 */
var colors = {"#5C8B93": "filter: invert(48%) sepia(57%) saturate(231%) hue-rotate(141deg) brightness(95%) contrast(88%);","#B03A48": "filter: invert(29%) sepia(27%) saturate(3713%) hue-rotate(324deg) brightness(87%) contrast(85%);","#D4804D": "filter: invert(47%) sepia(88%) saturate(325%) hue-rotate(339deg) brightness(102%) contrast(89%);","#E0C872": "filter: invert(98%) sepia(5%) saturate(4138%) hue-rotate(332deg) brightness(92%) contrast(91%);","#3E6958": "filter: invert(33%) sepia(57%) saturate(279%) hue-rotate(105deg) brightness(95%) contrast(85%);"};
var keys = Object.keys(colors);
document.querySelectorAll("#tango > img").forEach((e, k) => { e.setAttribute("style", colors[keys[k % keys.length]]) });
