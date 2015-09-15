<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" version="1.0">
	<xsl:output method="text" omit-xml-declaration="yes" indent="no"/>
	<xsl:template match="/">
		<xsl:apply-templates select="model"/>
	</xsl:template>
	<xsl:template match="model">
		<xsl:apply-templates select="page"/>
	</xsl:template>
	<xsl:template match="page">
		<xsl:apply-templates select="header"/>
		<xsl:apply-templates select="body"/>
		<xsl:apply-templates select="bottom"/>
	</xsl:template>

	<xsl:template match='body'>
		<xsl:apply-templates/>
	</xsl:template>

	<xsl:template match="header">
		<xsl:apply-templates/>
	</xsl:template>

	<xsl:template match="bottom">
		<xsl:apply-templates/>
<xsl:text>
</xsl:text>
	</xsl:template>

	<xsl:template match="text">
		<xsl:text>"</xsl:text><xsl:value-of select="normalize-space(.)"/><xsl:text>"</xsl:text>
	</xsl:template>

	<xsl:template match="table">
		<xsl:for-each select="columns">
			<xsl:for-each select="cell">
				<xsl:text>"</xsl:text><xsl:value-of select="normalize-space(.)"/><xsl:text>"</xsl:text><xsl:text>;</xsl:text>
			</xsl:for-each>
		</xsl:for-each>
<xsl:text>
</xsl:text>
		<xsl:for-each select="rows">
			<xsl:for-each select="cell">
				<xsl:if test="substring(normalize-space(text()),1,10) != 'data:image'">				 
					<xsl:text>"</xsl:text><xsl:value-of select="normalize-space(.)"/><xsl:text>"</xsl:text>
				</xsl:if>
				<xsl:text>;</xsl:text>
			</xsl:for-each>
<xsl:text>
</xsl:text>
		</xsl:for-each>
	</xsl:template>
	<xsl:template match="br"><xsl:text> </xsl:text></xsl:template>
	<xsl:template match="image"></xsl:template>
	
</xsl:stylesheet>
