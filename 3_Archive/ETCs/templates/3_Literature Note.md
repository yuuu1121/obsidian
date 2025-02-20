---
tags:
  - PaperReview
  - 
status: Literature
aliases: 
keywords: 
author: 
dg-publish: false
---

```ad-cite
{{bibliography}}
```

```ad-cite
**Contribution**::
```

```ad-info
title: {% for attachment in attachments | filterby("path", "endswith", ".pdf") %}[{{attachment.title}}]({{attachment.title}}) {% endfor %}
collapse: true

{% for creator in creators %}
{% if creator.name == null %}
**{{creator.creatorType | capitalize}}**:: {{creator.lastName}}, {{creator.firstName}}<br>
{% endif %}
{% if creator.name %}
**{{creator.creatorType | capitalize}}**:: {{creator.name}}<br>
{% endif %}
{% endfor %}

**Title**:: {{title}}

**Year**:: {{date | format("YYYY")}} 

**Citekey**:: @{{citekey}}

{% if allTags %}
**Tags**:: {{allTags}}
{% endif %}

{% if itemType %}
**itemType**:: {{itemType}}
{% endif %} 

{% if itemType == "journalArticle" %}
**Journal**:: *{{publicationTitle}}* 
{% endif %}

{% if volume %}
**Volume**:: {{volume}} 
{% endif %}

{% if issue %}
**Issue**:: {{issue}} 
{% endif %}

{% if itemType == "bookSection" %}
**Book**:: {{publicationTitle}} 
{% endif %}

{% if publisher %}
**Publisher**:: {{publisher}} 
{% endif %}

{% if publisher %}
**Publisher**:: {{publisher}} 
{% endif %}

{% if place %}
**Location**:: {{place}} 
{% endif %}  

{% if pages %} 
**Pages**:: {{pages}} 
{% endif %}  

{% if DOI %}
**DOI**:: {{DOI}} 
{% endif %}  

{% if ISBN %}
**ISBN**:: {{ISBN}}
{% endif %}
```

```ad-abstract
collapse: true
{% if abstractNote %}
abstract:: {{abstractNote}}
{% endif %}
```

<br><br>

# Annotations 

{% for annotation in annotations %}
{% if annotation.colorCategory == "Gray" %} 
## {{annotation.annotatedText | escape }}
{% elif annotation.colorCategory == "Orange" %}
### {{annotation.annotatedText | escape }}
{% elif annotation.colorCategory == "Magenta" %}
#### {{annotation.annotatedText | escape }}
{% else %}
```ad-note
{% if annotation.colorCategory == "Yellow" %}
title: <span style='color:yellow'> Highlight </span> - ([Go to Paper](zotero://open-pdf/library/items/{{annotation.attachment.itemKey}}?page={{annotation.page}}&annotation={{annotation.id}}))
{% elif annotation.colorCategory == "Red" %}
title: <span style='color:red'> Highlight </span> - ([Go to Paper](zotero://open-pdf/library/items/{{annotation.attachment.itemKey}}?page={{annotation.page}}&annotation={{annotation.id}}))
{% elif annotation.colorCategory == "Green" %}
title: <span style='color:greenyellow'> Highlight </span> - ([Go to Paper](zotero://open-pdf/library/items/{{annotation.attachment.itemKey}}?page={{annotation.page}}&annotation={{annotation.id}}))
{% elif annotation.colorCategory == "Blue" %}
title: <span style='color:blueviolet'> Highlight </span> - ([Go to Paper](zotero://open-pdf/library/items/{{annotation.attachment.itemKey}}?page={{annotation.page}}&annotation={{annotation.id}}))
{% elif annotation.colorCategory == "Purple" %}
title: <span style='color:violet'> Highlight </span> - ([Go to Paper](zotero://open-pdf/library/items/{{annotation.attachment.itemKey}}?page={{annotation.page}}&annotation={{annotation.id}}))
{% else %}
title: Note - ([Go to Paper](zotero://open-pdf/library/items/{{annotation.attachment.itemKey}}?page={{annotation.page}}&annotation={{annotation.id}}))
{% endif %}
{{annotation.annotatedText | escape }}
{% if annotation.imageRelativePath %}
[!Image]
<mark class="customZot-{{annotation.colorCategory}}"> Image</mark>
![{{annotation.imageRelativePath}}]({{annotation.imageRelativePath}})
{% endif %}
{% if annotation.comment %}
**Comment**:
{{annotation.comment}}
{% endif %}
```
{% endif %}
{% endfor %}