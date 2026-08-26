<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0">
    <xsl:output omit-xml-declaration="yes" indent="yes" encoding="utf-8" />

    <xsl:template match="node()|@*">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*" />
        </xsl:copy>
    </xsl:template>

    <xsl:template match="@xml:id">
        <xsl:variable name="attr-value-1">
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="." />
                <xsl:with-param name="replace" select="','" />
                <xsl:with-param name="with" select="'_comma_'" />
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable
            name="attr-value-2">
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="$attr-value-1" />
                <xsl:with-param name="replace" select="'*'" />
                <xsl:with-param name="with" select="'_asterisk_'" />
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable
            name="attr-value-3">
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="$attr-value-2" />
                <xsl:with-param name="replace" select="'@'" />
                <xsl:with-param name="with" select="'_at-sign_'" />
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable
            name="attr-value-4">
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="$attr-value-3" />
                <xsl:with-param name="replace" select="':'" />
                <xsl:with-param name="with" select="'_colon_'" />
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable
            name="attr-value-5">
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="$attr-value-4" />
                <xsl:with-param name="replace" select="'['" />
                <xsl:with-param name="with" select="'_left-square-bracket_'" />
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable
            name="attr-value-6">
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="$attr-value-5" />
                <xsl:with-param name="replace" select="']'" />
                <xsl:with-param name="with" select="'_right-square-bracket_'" />
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable
            name="attr-value-7">
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="$attr-value-6" />
                <xsl:with-param name="replace" select="'|'" />
                <xsl:with-param name="with" select="'_pipeline_'" />
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable
            name="attr-value-8">
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="$attr-value-7" />
                <xsl:with-param name="replace" select="'/'" />
                <xsl:with-param name="with" select="'_forward-slash_'" />
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable
            name="attr-value-9">
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="$attr-value-8" />
                <xsl:with-param name="replace" select="'('" />
                <xsl:with-param name="with" select="'_left-parenthesis_'" />
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable
            name="attr-value-10">
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="$attr-value-9" />
                <xsl:with-param name="replace" select="')'" />
                <xsl:with-param name="with" select="'_right-parenthesis_'" />
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable
            name="attr-value-11">
            <xsl:call-template name="replace-string">
                <xsl:with-param name="text" select="$attr-value-10" />
                <xsl:with-param name="replace" select="' '" />
                <xsl:with-param name="with" select="''" />
            </xsl:call-template>
        </xsl:variable>

        <xsl:attribute
            name="xml:id"><xsl:value-of select="$attr-value-11"></xsl:value-of>
        </xsl:attribute>

    </xsl:template>

    <xsl:template name="replace-string">
        <xsl:param name="text" />
        <xsl:param name="replace" />
        <xsl:param name="with" />
        <xsl:choose>
            <xsl:when test="contains($text,$replace)">
                <xsl:value-of select="substring-before($text,$replace)" />
            <xsl:value-of
                    select="$with" />
            <xsl:call-template name="replace-string">
                    <xsl:with-param name="text"
                        select="substring-after($text,$replace)" />
                    <xsl:with-param name="replace" select="$replace" />
                    <xsl:with-param name="with" select="$with" />
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$text" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


</xsl:stylesheet>

<!--
xsltproc ./modules/fix_xml-id/fix_xml-id.xslt ./1_sanskr/sa_vidyAkara-subhASitaratnakoza.xml > output.xml
-->