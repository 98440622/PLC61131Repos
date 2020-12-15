<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/1999/xhtml">
    <xsl:output method="xml" version="1.0" encoding="UTF-16" indent="yes" omit-xml-declaration="no" />
	<xsl:param name="prjTitle"/>
	<xsl:param name="prjDate"/>
	<xsl:param name="prjTime"/>
    <xsl:template match="/">
        <html>
        <head>
        <title>Project <xsl:value-of select="$prjTitle"/></title>
        <meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-16"/>
        <style type="text/css">
		body {
			text-align: center;
			background: white;
			color: #5b5d5e;
			margin: 0;
			padding: 0;
			font-family: Verdana, Arial, Helvetica, sans-serif; 
			font-size: 12px;
		}
		.head1{
			font-weight: bold;
			font-size: 14px;
		}
		.head0{
			font-weight: bold;
			font-size: 14px;
			text-decoration:underline;
		}
		.table1
		{
			border-style:solid;
			border-width:1px;
			margin-left:auto;
			margin-right:auto;
			margin-top: 0.5cm;
			border-collapse:collapse;
			width: 19cm;
		}
		.content
		{
			font-size: 12px;
			padding-left: 10px;
		}
		
		.contentBold
		{
			font-size: 12px;
			font-weight: bold;
		}
		
		.titlePage
		{
			background: #c1cc23;
			color: black;
			width : 100%;
			font-weight: bold;
			border-style:solid;
			border-width:1px;
			font-size: 14px;
		}
		
		.countCtrl
		{
			border-style:solid;
			border-width: 1px;
			background: #f6f8d8;
			font-size: 12px;
		}
		h1
		{
			margin-top: 1cm;
		}
		
		.borderRight
		{
			border-right: 1px solid black;
		}
        </style>
        </head>
        <body>
        <h1 align="center">User Interface Project:  <xsl:value-of select="$prjTitle"/></h1>
		<h3 align="center"> Last update: <xsl:value-of select="$prjDate"/> - <xsl:value-of select="$prjTime"/></h3>
		<h3 class="head0"> Project infos: </h3>
		<table align="center">
		<tr>
		<td class="head1">Number of pages: <xsl:value-of select="count( PRJ_RESOURCES/PAGES/PAGE )"/></td>
		</tr>
		<tr>
		<td class="head1">Languages:</td>
		</tr>
		<xsl:for-each select="PRJ_RESOURCES/LANGUAGES/LANG">
                <tr>
                    <td class="content">
                       - <xsl:value-of select="@descr"/>
                    </td>
                </tr>
        </xsl:for-each>
		<tr>
		<td class="head1">Start page: <xsl:value-of select="PRJ_RESOURCES/PAGES_INFO/FIRST_PAGE"/></td>
		</tr>
		</table>
		<p> <h3 class="head0" > Page Infos: </h3>
		<xsl:if test="count( PRJ_RESOURCES/FRAMESET ) > 0">
		<table class="table1">
			<tr class="titlePage">
                <td>Frameset</td>
				<td colspan="4"></td>
			</tr>
			<tr>
                <td colspan="4" class="borderRight"><img src="docImages\Frame set.bmp" alt="Frame set.bmp" width="300px"/></td>
				<td><xsl:value-of select="ATTRIBUTES/DESC"/></td>
			</tr>
		</table>
		</xsl:if>
		
		<xsl:for-each select="PRJ_RESOURCES/PAGES/PAGE">
			<table class="table1">
			<tr class="titlePage">
                <td><xsl:value-of select="@name"/></td>
				<td colspan="4"></td>
			</tr>
			<tr>
                <td colspan="4" class="borderRight"><img src="docImages\{@name}.bmp" alt="{@name}.bmp" width="300px"/></td>
				<td><xsl:value-of select="ATTRIBUTES/DESC"/></td>
			</tr>
			<xsl:if test="count( OBJECTS/PROGRESSES/PROGRESS ) > 0">
			<tr class="countCtrl">
			<td colspan="5">Progresses: <xsl:value-of select="count( OBJECTS/PROGRESSES/PROGRESS )"/></td>
			</tr>
			<xsl:for-each select="OBJECTS/PROGRESSES/PROGRESS">
			<tr>
			<td class="contentBold" ><xsl:value-of select="@name"/></td>
			<td class="content"><xsl:value-of select="DESC"/></td>
			<td class="content" >Min: <xsl:value-of select="VARMIN"/></td>
			<td class="content" >Max: <xsl:value-of select="VARMAX"/></td>
			<td class="content">Var: <xsl:value-of select="VAR"/></td>	
			</tr>
			</xsl:for-each>
			</xsl:if>
			<xsl:if test="count( OBJECTS/EDITS/EDIT ) > 0">
			<tr class="countCtrl">
			<td colspan="5"> Edits: <xsl:value-of select="count( OBJECTS/EDITS/EDIT )"/></td>
			</tr>
			<xsl:for-each select="OBJECTS/EDITS/EDIT">
			<tr>
			<td class="contentBold" ><xsl:value-of select="@name"/></td>
			<td class="content"><xsl:value-of select="DESC"/></td>
			<td class="content">Min: <xsl:value-of select="VARMIN"/></td>
			<td class="content">Max: <xsl:value-of select="VARMAX"/></td>
			<td class="content">Var: <xsl:value-of select="VAR"/></td>				
			</tr>
			</xsl:for-each>
			</xsl:if>
			</table>
        </xsl:for-each>
		</p>
        </body>
        </html>
    </xsl:template>
</xsl:stylesheet>